'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

interface EvaluationMetrics {
    faithfulness?: number;
    answer_relevance?: number;
    context_precision?: number;
    context_recall?: number;
    overall_score?: number;
}

interface LLMJudgeResult {
    accuracy_score: number;
    completeness_score: number;
    consistency_score: number;
    overall_score: number;
    reasoning: string;
}

interface MetricsPanelProps {
    evaluationMetrics?: EvaluationMetrics;
    llmJudge?: LLMJudgeResult;
}

export default function MetricsPanel({ evaluationMetrics, llmJudge }: MetricsPanelProps) {
    if (!evaluationMetrics && !llmJudge) {
        return null;
    }

    // Prepare RAG metrics data
    const ragMetricsData = evaluationMetrics ? [
        { name: 'Faithfulness', score: (evaluationMetrics.faithfulness || 0) * 100 },
        { name: 'Relevance', score: (evaluationMetrics.answer_relevance || 0) * 100 },
        { name: 'Precision', score: (evaluationMetrics.context_precision || 0) * 100 },
        { name: 'Recall', score: (evaluationMetrics.context_recall || 0) * 100 },
    ] : [];

    // Prepare LLM Judge data
    const llmJudgeData = llmJudge ? [
        { name: 'Accuracy', score: llmJudge.accuracy_score * 100 },
        { name: 'Completeness', score: llmJudge.completeness_score * 100 },
        { name: 'Consistency', score: llmJudge.consistency_score * 100 },
    ] : [];

    const getBarColor = (score: number) => {
        if (score >= 80) return '#22c55e'; // Green
        if (score >= 60) return '#f59e0b'; // Orange
        return '#ef4444'; // Red
    };

    return (
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Evaluation Metrics</h2>

            <div className="grid md:grid-cols-2 gap-8">
                {/* RAG Metrics */}
                {evaluationMetrics && (
                    <div>
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">RAG Performance</h3>
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={ragMetricsData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                                <Tooltip
                                    formatter={(value: number) => `${value.toFixed(1)}%`}
                                    contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                                />
                                <Bar dataKey="score" radius={[8, 8, 0, 0]}>
                                    {ragMetricsData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={getBarColor(entry.score)} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>

                        {evaluationMetrics.overall_score !== undefined && (
                            <div className="mt-4 p-3 bg-primary-50 rounded-lg">
                                <div className="flex justify-between items-center">
                                    <span className="text-sm font-medium text-gray-700">Overall Score</span>
                                    <span className="text-2xl font-bold text-primary-700">
                                        {(evaluationMetrics.overall_score * 100).toFixed(1)}%
                                    </span>
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* LLM Judge */}
                {llmJudge && (
                    <div>
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">LLM-as-Judge</h3>
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={llmJudgeData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                                <Tooltip
                                    formatter={(value: number) => `${value.toFixed(1)}%`}
                                    contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                                />
                                <Bar dataKey="score" radius={[8, 8, 0, 0]}>
                                    {llmJudgeData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={getBarColor(entry.score)} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>

                        <div className="mt-4 p-3 bg-success-50 rounded-lg">
                            <div className="flex justify-between items-center mb-2">
                                <span className="text-sm font-medium text-gray-700">Judge Score</span>
                                <span className="text-2xl font-bold text-success-700">
                                    {(llmJudge.overall_score * 100).toFixed(1)}%
                                </span>
                            </div>
                            <p className="text-xs text-gray-600 mt-2">{llmJudge.reasoning}</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
