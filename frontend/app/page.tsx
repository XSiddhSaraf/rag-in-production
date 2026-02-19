import FileUpload from '@/components/FileUpload';
import { Shield } from 'lucide-react';

export default function Home() {
    return (
        <main className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-100">
            <div className="container mx-auto px-4 py-12">
                {/* Header */}
                <div className="text-center mb-12 animate-fade-in">
                    <div className="flex items-center justify-center gap-3 mb-4">
                        <Shield className="h-12 w-12 text-primary-600" />
                        <h1 className="text-5xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
                            EU AI Act Compliance Analyzer
                        </h1>
                    </div>
                    <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                        Analyze your technical documentation for compliance with the EU AI Act.
                        Upload your project document and receive a comprehensive risk assessment.
                    </p>
                </div>

                {/* Upload Section */}
                <div className="mb-12 animate-slide-up">
                    <FileUpload />
                </div>

                {/* Info Cards */}
                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto animate-fade-in" style={{ animationDelay: '0.2s' }}>
                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                        <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                            <span className="text-2xl">🔍</span>
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-2">Smart Analysis</h3>
                        <p className="text-sm text-gray-600">
                            Advanced RAG pipeline analyzes your documents against the EU AI Act using state-of-the-art AI
                        </p>
                    </div>

                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                        <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center mb-4">
                            <span className="text-2xl">📊</span>
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-2">Detailed Reports</h3>
                        <p className="text-sm text-gray-600">
                            Get comprehensive Excel reports with risk classifications and EU AI Act references
                        </p>
                    </div>

                    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                        <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center mb-4">
                            <span className="text-2xl">✅</span>
                        </div>
                        <h3 className="font-semibold text-gray-900 mb-2">Quality Metrics</h3>
                        <p className="text-sm text-gray-600">
                            RAG evaluation metrics and LLM-as-judge validation ensure accurate results
                        </p>
                    </div>
                </div>

                {/* Footer */}
                <div className="text-center mt-16 text-gray-500 text-sm">
                    <p>Production-grade RAG application • Powered by Azure OpenAI</p>
                </div>
            </div>
        </main>
    );
}
