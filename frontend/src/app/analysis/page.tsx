"use client";

import { useState, useEffect } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchAnalysis } from "@/lib/api";

export default function AnalysisPage() {
    const [analysis, setAnalysis] = useState<any | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const getAnalysis = async () => {
            try {
                const data = await fetchAnalysis();
                setAnalysis(data);
            } catch (err) {
                setError(
                    "An error occurred while fetching the analysis. Please try again later."
                );
                console.error("Fetch error:", err);
            } finally {
                setLoading(false);
            }
        };

        getAnalysis();
    }, []);

    const renderAnalysis = (analysis: any) => {
        try {
            const parsedAnalysis = JSON.parse(analysis.analysis);
            return (
                <div className="space-y-4">
                    <h3 className="text-lg font-semibold">Analysis Result:</h3>
                    <p>
                        <strong>Filename:</strong> {parsedAnalysis.filename}
                    </p>
                    <p>
                        <strong>Summary:</strong> {parsedAnalysis.summary}
                    </p>
                    <div>
                        <h4 className="font-semibold">Statistics:</h4>
                        <p>
                            <strong>Word Count:</strong>{" "}
                            {parsedAnalysis.statistics.word_count}
                        </p>
                        <p>
                            <strong>Sentence Count:</strong>{" "}
                            {parsedAnalysis.statistics.sentence_count}
                        </p>
                        <p>
                            <strong>Compression Ratio:</strong>{" "}
                            {parsedAnalysis.statistics.compression_ratio}
                        </p>
                    </div>
                </div>
            );
        } catch (error) {
            console.error("Error parsing analysis JSON:", error);
            return <p className="text-red-500">Error parsing analysis data.</p>;
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-6">Text Analysis</h1>
            <Card className="w-full">
                <CardHeader>
                    <CardTitle>Document Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <AnalysisSkeleton />
                    ) : error ? (
                        <p className="text-red-500">{error}</p>
                    ) : analysis ? (
                        renderAnalysis(analysis)
                    ) : (
                        <p className="text-gray-500">No analysis available.</p>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}

function AnalysisSkeleton() {
    return (
        <div className="space-y-4">
            <div>
                <Skeleton className="h-4 w-1/4 mb-2" />
                <Skeleton className="h-4 w-3/4" />
            </div>
            <div>
                <Skeleton className="h-4 w-1/4 mb-2" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
            </div>
        </div>
    );
}
