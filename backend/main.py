from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import numpy as np
from datetime import datetime

load_dotenv('.env')

app = FastAPI(title="漢方AI診断API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    id: str
    text: str
    isBot: bool
    timestamp: str

class ChatRequest(BaseModel):
    message: str
    messages: List[Message]

class ChatResponse(BaseModel):
    message: str
    diagnosis: Optional[Dict[str, Any]] = None

class KanpoAI:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=api_key
        )
        self.symptoms_data = self.load_symptoms_data()
        self.diagnosis_data = self.load_diagnosis_data()
        self.conversation_state = {}
        
        # 診断フローの状態管理
        self.diagnosis_flow = {
            "phase": "initial",  # initial, questioning, analysis, recommendation
            "collected_symptoms": [],
            "symptom_scores": {},
            "current_category": None,
            "asked_questions": []
        }
        
    def load_symptoms_data(self):
        try:
            with open('shojo.json', 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip().startswith('symptoms = []'):
                    return self.parse_python_symptoms(content)
                else:
                    return json.loads(content)
        except FileNotFoundError:
            return []
    
    def load_diagnosis_data(self):
        try:
            with open('shindan.json', 'r', encoding='utf-8') as f:
                return json.loads(f.read())
        except FileNotFoundError:
            return {"recipes": [], "logic_rules": []}
    
    def parse_python_symptoms(self, content):
        m_questions = [
            ("M1", "寝つきが悪く、夜中に目が覚める", "自律神経", "安眠ゆるり蒸し"),
            ("M2", "緊張しやすく、心配ごとが頭から離れない", "自律神経", "安眠ゆるり蒸し"),
            ("M3", "朝が苦手で、ぼーっとしてしまう", "自律神経", "安眠ゆるり蒸し"),
            ("M4", "急にイライラしたり涙が出たり、情緒が不安定になる", "自律神経", "安眠ゆるり蒸し"),
            ("M5", "音や光に敏感になりやすい", "自律神経", "安眠ゆるり蒸し"),
            ("M6", "月経のリズムが安定しない", "ホルモン", "リズム巡り蒸し"),
            ("M7", "更年期症状が気になる（ほてり、イライラなど）", "ホルモン", "リズム巡り蒸し"),
            ("M8", "月経前に胸の張りや気分の波がある", "ホルモン", "リズム巡り蒸し"),
            ("M9", "月経痛が強い or 急に重くなった", "ホルモン", "リズム巡り蒸し"),
            ("M10", "花粉症・鼻炎・アトピーなどがある", "免疫", "デトックス蒸し"),
            ("M11", "アレルギーや自己免疫に関する不調がある", "免疫", "デトックス蒸し"),
        ]
        
        f_questions = [
            ("F1", "疲れやすく、だるさが取れない", "気", "安眠ゆるり蒸し"),
            ("F2", "ため息が多く、やる気が出ない", "気", "リズム巡り蒸し"),
            ("F3", "お腹が張りやすく、ガスがたまりやすい", "気", "リズム巡り蒸し"),
            ("F4", "顔色が悪く、肌が乾燥しやすい", "血", "リズム巡り蒸し"),
            ("F5", "月経の血量が少ない／色が薄い", "血", "リズム巡り蒸し"),
            ("F6", "肩こり・冷え性・経血に塊がある", "血（瘀血）", "リズム巡り蒸し"),
            ("F7", "唇や爪の色が白っぽくなる", "血", "リズム巡り蒸し"),
            ("F8", "むくみやすく、身体が重だるい", "水", "デトックス蒸し"),
            ("F9", "トイレが近い／汗が多い or 少ない", "水", "デトックス蒸し"),
            ("F10", "舌の周りに歯の痕がつきやすい", "水（脾虚）", "デトックス蒸し"),
            ("F11", "のどが渇くのに水を飲みたくない", "水（津液失調）", "デトックス蒸し"),
            ("F12", "抜け毛や白髪が気になる", "精（腎精）", "安眠ゆるり蒸し"),
            ("F13", "眠りが浅く、夢をよく見る", "精", "安眠ゆるり蒸し"),
            ("F14", "老化や生殖力の衰えを感じる", "精", "安眠ゆるり蒸し"),
            ("F15", "耳鳴り・難聴・めまいがある", "精（腎虚）", "安眠ゆるり蒸し"),
            ("F16", "腰や膝に力が入らない・だるい", "精（腎虚）", "安眠ゆるり蒸し"),
        ]
        
        symptoms = []
        for code, text, category, recipe in m_questions + f_questions:
            symptoms.append({
                "id": code,
                "title": text,
                "type": "症状",
                "functions": [category],
                "related_recipe": [recipe],
                "description": f"{text} という症状は、{category}の乱れに関係しており、{recipe}によるケアが有効とされています。"
            })
        
        return symptoms
    
    def get_structured_questions(self) -> List[Dict[str, Any]]:
        """構造化された質問リストを生成"""
        questions = []
        
        # Phase 1: 基本的な体調について
        basic_questions = [
            {
                "id": "basic_energy",
                "question": "最近の体調はいかがですか？疲れやだるさを感じることが多いですか？",
                "category": "基本",
                "keywords": ["疲れ", "だるい", "元気", "体調"]
            },
            {
                "id": "sleep_quality", 
                "question": "睡眠の状態はいかがですか？寝つきの悪さや夜中に目が覚めることはありますか？",
                "category": "自律神経",
                "keywords": ["眠り", "睡眠", "寝つき", "目が覚める"]
            }
        ]
        
        # Phase 2: カテゴリ別詳細質問
        category_questions = {
            "ホルモン": [
                "月経周期に変化はありますか？（不順、痛み、量の変化など）",
                "更年期症状（ほてり、イライラ、発汗など）を感じることはありますか？",
                "月経前に胸の張りや気分の変化はありますか？"
            ],
            "自律神経": [
                "ストレスを感じやすく、緊張することが多いですか？",
                "音や光に敏感になることはありますか？",
                "朝起きるのが辛く、ぼーっとしてしまうことはありますか？"
            ],
            "免疫": [
                "花粉症やアレルギー症状はありますか？",
                "風邪をひきやすい、または治りにくいことはありますか？",
                "皮膚トラブル（アトピー、湿疹など）はありますか？"
            ],
            "血": [
                "顔色が悪い、または肌が乾燥しやすいですか？",
                "肩こりや冷え性に悩んでいますか？",
                "爪や唇の色が白っぽくなることはありますか？"
            ],
            "水": [
                "むくみやすく、身体が重だるく感じますか？",
                "トイレの回数が多い、または汗のかき方に変化はありますか？",
                "のどが渇くのに水を飲みたくないことはありますか？"
            ],
            "気": [
                "ため息が多く、やる気が出ないことはありますか？",
                "お腹が張りやすく、ガスがたまりやすいですか？"
            ],
            "精": [
                "抜け毛や白髪が気になりますか？",
                "耳鳴りやめまいを感じることはありますか？",
                "腰や膝に力が入らない、だるいと感じますか？"
            ]
        }
        
        return basic_questions, category_questions

    def analyze_symptoms(self, user_input: str, conversation_history: List[Message]) -> Dict[str, Any]:
        # 症状マッチングスコア計算（改良版）
        symptom_scores = {}
        matched_symptoms = []
        
        # より詳細なキーワードマッチング
        for symptom in self.symptoms_data:
            score = 0
            symptom_title = symptom["title"]
            symptom_keywords = symptom_title.split("、") + symptom_title.split("・") + symptom_title.split("／")
            
            # 部分一致での検索を改良
            for keyword in symptom_keywords:
                keyword = keyword.strip()
                if len(keyword) > 1 and keyword in user_input:
                    score += 1
            
            # 関連キーワードも検索
            related_keywords = {
                "疲れ": ["だるい", "疲労", "元気がない", "しんどい"],
                "眠り": ["睡眠", "寝る", "不眠", "寝つき"],
                "月経": ["生理", "月のもの", "メンス"],
                "更年期": ["ホットフラッシュ", "のぼせ"],
                "むくみ": ["浮腫", "腫れ", "パンパン"],
                "肩こり": ["首こり", "肩が重い", "凝り"]
            }
            
            for main_keyword, related in related_keywords.items():
                if main_keyword in symptom_title:
                    for related_keyword in related:
                        if related_keyword in user_input:
                            score += 1
            
            if score > 0:
                category = symptom["functions"][0]
                if category not in symptom_scores:
                    symptom_scores[category] = 0
                symptom_scores[category] += score
                matched_symptoms.append(symptom)
        
        # 診断ロジックの適用
        diagnosis_result = self.apply_diagnosis_logic(symptom_scores)
        
        return {
            "symptom_scores": symptom_scores,
            "recommended_recipe": diagnosis_result["recommended_recipe"],
            "matched_symptoms": matched_symptoms,
            "diagnosis_confidence": diagnosis_result["confidence"],
            "next_questions": diagnosis_result["next_questions"]
        }
    
    def apply_diagnosis_logic(self, symptom_scores: Dict[str, int]) -> Dict[str, Any]:
        """診断ロジックを適用"""
        if not symptom_scores:
            return {
                "recommended_recipe": None,
                "confidence": "low",
                "next_questions": ["基本的な体調について詳しく教えてください"]
            }
        
        # スコア合算ロジック（rule_004）
        category_groups = {
            "リズム巡り蒸し": symptom_scores.get("ホルモン", 0) + symptom_scores.get("血", 0) + symptom_scores.get("血（瘀血）", 0),
            "デトックス蒸し": symptom_scores.get("免疫", 0) + symptom_scores.get("水", 0) + symptom_scores.get("水（脾虚）", 0) + symptom_scores.get("水（津液失調）", 0),
            "安眠ゆるり蒸し": symptom_scores.get("自律神経", 0) + symptom_scores.get("精", 0) + symptom_scores.get("精（腎精）", 0) + symptom_scores.get("精（腎虚）", 0) + symptom_scores.get("気", 0)
        }
        
        # 最高スコアのレシピを特定
        max_score = max(category_groups.values())
        top_recipes = [recipe for recipe, score in category_groups.items() if score == max_score]
        
        # 単一レシピ推奨ロジック（rule_001）
        if len(top_recipes) == 1 and max_score >= 2:
            recommended_recipe_name = top_recipes[0]
            confidence = "high"
        # 複数レシピ混合推奨ロジック（rule_002）
        elif len(top_recipes) > 1:
            recommended_recipe_name = top_recipes[0]  # 最初の候補
            confidence = "medium"
        # 低スコア時のアドバイス（rule_003）
        else:
            recommended_recipe_name = None
            confidence = "low"
        
        # 対応するレシピ詳細を取得
        recommended_recipe = None
        if recommended_recipe_name:
            for recipe in self.diagnosis_data.get("recipes", []):
                if recipe["title"] == recommended_recipe_name:
                    recommended_recipe = recipe
                    break
        
        # 次の質問を生成
        next_questions = self.generate_next_questions(symptom_scores, confidence)
        
        return {
            "recommended_recipe": recommended_recipe,
            "confidence": confidence,
            "next_questions": next_questions
        }
    
    def generate_next_questions(self, symptom_scores: Dict[str, int], confidence: str) -> List[str]:
        """次に聞くべき質問を生成"""
        questions = []
        
        if confidence == "low":
            questions = [
                "どのような症状が一番お辛いですか？",
                "症状はいつ頃から始まりましたか？",
                "日常生活で困っていることはありますか？"
            ]
        elif confidence == "medium":
            # スコアが低いカテゴリについて詳しく聞く
            low_score_categories = [cat for cat, score in symptom_scores.items() if score == 0]
            if "ホルモン" in low_score_categories:
                questions.append("月経周期や更年期症状について詳しく教えてください")
            if "水" in low_score_categories:
                questions.append("むくみや水分の取り方について教えてください")
            if "自律神経" in low_score_categories:
                questions.append("睡眠やストレスの状況について教えてください")
        
        return questions[:2]  # 最大2問まで
    
    def get_recommended_recipe(self, symptom_scores: Dict[str, int]) -> Dict[str, Any]:
        if not symptom_scores:
            return None
        
        # スコアに基づいてレシピを決定
        max_score = max(symptom_scores.values())
        top_categories = [cat for cat, score in symptom_scores.items() if score == max_score]
        
        recipe_mapping = {
            "自律神経": "安眠ゆるり蒸し",
            "ホルモン": "リズム巡り蒸し",
            "免疫": "デトックス蒸し",
            "気": "安眠ゆるり蒸し",
            "血": "リズム巡り蒸し",
            "血（瘀血）": "リズム巡り蒸し",
            "水": "デトックス蒸し",
            "水（脾虚）": "デトックス蒸し",
            "水（津液失調）": "デトックス蒸し",
            "精": "安眠ゆるり蒸し",
            "精（腎精）": "安眠ゆるり蒸し",
            "精（腎虚）": "安眠ゆるり蒸し"
        }
        
        recommended_recipe_name = recipe_mapping.get(top_categories[0], "安眠ゆるり蒸し")
        
        # 対応するレシピ詳細を取得
        recipe_detail = None
        for recipe in self.diagnosis_data.get("recipes", []):
            if recipe["title"] == recommended_recipe_name:
                recipe_detail = recipe
                break
        
        return recipe_detail
    
    async def generate_response(self, user_input: str, conversation_history: List[Message]) -> str:
        # 症状分析
        analysis = self.analyze_symptoms(user_input, conversation_history)
        
        # 会話履歴の構築
        history_text = "\n".join([
            f"{'ユーザー' if not msg.isBot else 'AI'}: {msg.text}" 
            for msg in conversation_history[-5:]  # 最新5件
        ])
        
        # 構造化質問の取得
        basic_questions, category_questions = self.get_structured_questions()
        
        # 診断の信頼度に基づいた応答戦略
        confidence = analysis.get("diagnosis_confidence", "low")
        recommended_recipe = analysis.get("recommended_recipe")
        next_questions = analysis.get("next_questions", [])
        
        # システムプロンプト（構造化質問対応版）
        system_prompt = f"""
あなたは漢方専門のAI診断システムです。shindanファイルのロジックに基づいて診断を行います。

診断データ（shindan.json）:
{json.dumps(self.diagnosis_data, ensure_ascii=False, indent=2)}

現在の症状分析結果:
- 症状スコア: {analysis.get('symptom_scores', {})}
- 診断信頼度: {confidence}
- 推奨レシピ: {recommended_recipe['title'] if recommended_recipe else 'なし'}
- 次の質問候補: {next_questions}

応答ガイドライン:
1. 診断信頼度が'low'の場合:
   - より詳細な症状を聞き出すための質問を行う
   - 基本的な体調について優しく聞く
   
2. 診断信頼度が'medium'の場合:
   - 暫定的な診断結果を伝える
   - 確認のため追加質問を1-2個行う
   
3. 診断信頼度が'high'の場合:
   - 明確な診断結果と推奨レシピを提示
   - 生薬の効能と使用方法を詳しく説明
   - 生活習慣のアドバイスも含める

4. 質問の仕方:
   - 選択肢を提供する（はい/いいえで答えやすく）
   - 複数の症状を一度に聞かない
   - 専門用語は分かりやすく説明

5. レシピ提案時の必須要素:
   - レシピ名と効果の説明
   - 含まれる生薬とその効能
   - 使用方法（蒸し方、頻度等）
   - 期待できる改善効果
   - 注意事項

親しみやすく、寄り添う姿勢で対応してください。
"""

        # LLMに送信するメッセージ
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"会話履歴:\n{history_text}\n\n新しいユーザー入力: {user_input}")
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            return f"申し訳ございません。システムエラーが発生しました: {str(e)}"

kanpo_ai = KanpoAI()

@app.get("/")
async def root():
    return {"message": "漢方AI診断APIへようこそ"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response_text = await kanpo_ai.generate_response(request.message, request.messages)
        
        return ChatResponse(
            message=response_text,
            diagnosis=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)