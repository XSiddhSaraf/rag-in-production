'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import RiskCard from '@/components/RiskCard';
import MetricsPanel from '@/components/MetricsPanel';
import { Download, ArrowLeft, Loader2, CheckCircle2, XCircle, Bot, Shield } from 'lucide-react';

interface Risk {
    description: string;
    category: string;
    level: string;
    eu_act_reference?: string;
    confidence_score?: number;
}

interface ProjectAnalysis {
    project_name: string;
    description: string;
    contains_ai: boolean;
    ai_confidence: number;
    high_risks: Risk[];
    low_risks: Risk[];
}

interface AnalysisResult {
    job_id: string;
    status: string;
    project_analysis?: ProjectAnalysis;
    evaluation_metrics?: any;
    llm_judge_result?: any;
    error_message?: string;
}

export default function DashboardPage() {
    const params = useParams();
    const router = useRouter();
    const jobId = params.jobId as string;

    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isDownloading, setIsDownloading] = useState(false);

    useEffect(() => {
        if (!jobId) return;

        const fetchResults = async () => {
            try {
                const data = await apiClient.getAnalysis(jobId);
                setResult(data);

                // Poll if still processing
                if (data.status === 'pending' || data.status === 'processing') {
                    setTimeout(fetchResults, 3000); // Poll every 3 seconds
                } else {
                    setIsLoading(false);
                }
            } catch (error) {
                console.error('Failed to fetch results:', error);
                setIsLoading(false);
            }
        };

        fetchResults();
    }, [jobId]);

    const handleDownload = async () => {
        setIsDownloading(true);
        try {
            const blob = await apiClient.downloadExcel(jobId);
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${result?.project_analysis?.project_name || 'analysis'}_report.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Download failed:', error);
            alert('Failed to download Excel file. Please try again.');
        } finally {
            setIsDownloading(false);
        }
    };

    if (isLoading || !result) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-100 flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="h-16 w-16 animate-spin text-primary-600 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Analyzing Document...</h2>
                    <p className="text-gray-600">This may take a minute. Please wait.</p>
                    {result?.status && (
                        <p className="text-sm text-primary-600 mt-4 font-medium">
                            Status: {result.status.replace('_', ' ').toUpperCase()}
                        </p>
                    )}
                </div>
            </div>
        );
    }

    if (result.status === 'failed') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-danger-50 via-white to-danger-100 flex items-center justify-center p-4">
                <div className="text-center max-w-md">
                    <XCircle className="h-16 w-16 text-danger-600 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Failed</h2>
                    <p className="text-gray-600 mb-4">{result.error_message || 'An unexpected error occurred.'}</p>
                    <button
                        onClick={() => router.push('/')}
                        className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    const analysis = result.project_analysis!;

    return (
        <main className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-100">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-8 flex items-center justify-between">
                    <button
                        onClick={() => router.push('/')}
                        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
                    >
                        <ArrowLeft className="h-5 w-5" />
                        <span>Back to Upload</span>
                    </button>

                    <button
                        onClick={handleDownload}
                        disabled={isDownloading}
                        className="flex items-center gap-2 px-6 py-3 bg-success-600 text-white rounded-lg hover:bg-success-700 transition-colors disabled:bg-gray-400"
                    >
                        <Download className="h-5 w-5" />
                        {isDownloading ? 'Downloading...' : 'Download Excel Report'}
                    </button>
                </div>

                {/* Success Banner */}
                <div className="bg-success-50 border border-success-200 rounded-xl p-6 mb-8 flex items-center gap-4 animate-fade-in">
                    <CheckCircle2 className="h-8 w-8 text-success-600 flex-shrink-0" />
                    <div>
                        <h3 className="font-semibold text-success-900 text-lg">Analysis Complete!</h3>
                        <p className="text-success-700 text-sm">Your document has been successfully analyzed against the EU AI Act.</p>
                    </div>
                </div>

                {/* Project Summary */}
                <div className="bg-white rounded-xl shadow-sm p-8 mb-8 border border-gray-200 animate-slide-up">
                    <div className="flex items-start justify-between mb-6">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900 mb-2">{analysis.project_name}</h1>
                            <p className="text-gray-600 leading-relaxed">{analysis.description}</p>
                        </div>
                        <Shield className="h-12 w-12 text-primary-600 flex-shrink-0" />
                    </div>

                    <div className="grid md:grid-cols-3 gap-6">
                        {/* AI Detection */}
                        <div className={`p-4 rounded-lg border-2 ${analysis.contains_ai ? 'bg-primary-50 border-primary-200' : 'bg-gray-50 border-gray-200'}`}>
                            <div className="flex items-center gap-2 mb-2">
                                <Bot className={`h-5 w-5 ${analysis.contains_ai ? 'text-primary-600' : 'text-gray-400'}`} />
                                <span className="font-semibold text-gray-900">Contains AI</span>
                            </div>
                            <p className={`text-2xl font-bold ${analysis.contains_ai ? 'text-primary-700' : 'text-gray-600'}`}>
                                {analysis.contains_ai ? 'YES' : 'NO'}
                            </p>
                            <p className="text-sm text-gray-600 mt-1">
                                Confidence: {(analysis.ai_confidence * 100).toFixed(0)}%
                            </p>
                        </div>

                        {/* High Risks */}
                        <div className="p-4 rounded-lg border-2 bg-danger-50 border-danger-200">
                            <span className="font-semibold text-gray-900 block mb-2">High Risks</span>
                            <p className="text-4xl font-bold text-danger-700">{analysis.high_risks.length}</p>
                        </div>

                        {/* Low Risks */}
                        <div className="p-4 rounded-lg border-2 bg-warning-50 border-warning-200">
                            <span className="font-semibold text-gray-900 block mb-2">Low Risks</span>
                            <p className="text-4xl font-bold text-warning-700">{analysis.low_risks.length}</p>
                        </div>
                    </div>
                </div>

                {/* Risks Section */}
                <div className="grid md:grid-cols-2 gap-8 mb-8">
                    {/* High Risks */}
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">High Risks</h2>
                        {analysis.high_risks.length > 0 ? (
                            <div className="space-y-4">
                                {analysis.high_risks.map((risk, idx) => (
                                    <RiskCard key={idx} risk={risk} index={idx} />
                                ))}
                            </div>
                        ) : (
                            <div className="bg-success-50 border border-success-200 rounded-lg p-6 text-center">
                                <CheckCircle2 className="h-12 w-12 text-success-600 mx-auto mb-2" />
                                <p className="text-success-700 font-medium">No high risks identified</p>
                            </div>
                        )}
                    </div>

                    {/* Low Risks */}
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">Low Risks</h2>
                        {analysis.low_risks.length > 0 ? (
                            <div className="space-y-4">
                                {analysis.low_risks.map((risk, idx) => (
                                    <RiskCard key={idx} risk={risk} index={idx} />
                                ))}
                            </div>
                        ) : (
                            <div className="bg-success-50 border border-success-200 rounded-lg p-6 text-center">
                                <CheckCircle2 className="h-12 w-12 text-success-600 mx-auto mb-2" />
                                <p className="text-success-700 font-medium">No low risks identified</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Evaluation Metrics */}
                {(result.evaluation_metrics || result.llm_judge_result) && (
                    <MetricsPanel
                        evaluationMetrics={result.evaluation_metrics}
                        llmJudge={result.llm_judge_result}
                    />
                )}
            </div>
        </main>
    );
}
