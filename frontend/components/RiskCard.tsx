'use client';

import { AlertTriangle, ShieldAlert, Info } from 'lucide-react';

interface Risk {
    description: string;
    category: string;
    level: string;
    eu_act_reference?: string;
    confidence_score?: number;
}

interface RiskCardProps {
    risk: Risk;
    index: number;
}

export default function RiskCard({ risk, index }: RiskCardProps) {
    const isHighRisk = risk.level === 'high';

    return (
        <div
            className={`
        p-5 rounded-lg border-l-4 transition-all duration-300 hover:shadow-md
        ${isHighRisk
                    ? 'bg-danger-50 border-danger-500'
                    : 'bg-warning-50 border-warning-500'
                }
        animate-slide-up
      `}
            style={{ animationDelay: `${index * 0.1}s` }}
        >
            <div className="flex items-start gap-3">
                {isHighRisk ? (
                    <ShieldAlert className="h-6 w-6 text-danger-600 flex-shrink-0 mt-1" />
                ) : (
                    <AlertTriangle className="h-6 w-6 text-warning-600 flex-shrink-0 mt-1" />
                )}

                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                        <span
                            className={`
                inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold
                ${isHighRisk ? 'bg-danger-200 text-danger-800' : 'bg-warning-200 text-warning-800'}
              `}
                        >
                            {isHighRisk ? 'HIGH RISK' : 'LOW RISK'}
                        </span>
                        <span className="text-xs text-gray-600">{risk.category}</span>
                    </div>

                    <p className="text-sm text-gray-800 mb-3 leading-relaxed">
                        {risk.description}
                    </p>

                    <div className="flex items-center gap-4 text-xs">
                        {risk.eu_act_reference && (
                            <div className="flex items-center gap-1 text-gray-600">
                                <Info className="h-3.5 w-3.5" />
                                <span className="font-medium">{risk.eu_act_reference}</span>
                            </div>
                        )}

                        {risk.confidence_score !== undefined && (
                            <div className="flex items-center gap-1">
                                <span className="text-gray-500">Confidence:</span>
                                <span className="font-semibold text-gray-700">
                                    {(risk.confidence_score * 100).toFixed(0)}%
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
