export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-sm">漢</span>
            </div>
            <h1 className="text-xl font-semibold text-gray-800">
              漢方AI診断
            </h1>
          </div>
          <nav className="hidden md:flex space-x-6">
            <a href="#" className="text-gray-600 hover:text-green-600 transition-colors">
              診断開始
            </a>
            <a href="#" className="text-gray-600 hover:text-green-600 transition-colors">
              漢方について
            </a>
            <a href="#" className="text-gray-600 hover:text-green-600 transition-colors">
              お問い合わせ
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}