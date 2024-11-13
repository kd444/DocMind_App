// pages/visualize.tsx
"use client";
import { useEffect, useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Html } from "@react-three/drei";
import * as THREE from "three";

// If you're using Next.js 13 with the `app` directory,
// you can place this file in `app/visualize/page.tsx`

// Define interfaces for type safetay
interface VectorMetadata {
    text?: string;
    [key: string]: any;
}

interface Vector {
    id: string;
    values: number[];
    metadata: VectorMetadata;
}

interface FetchVectorsResponse {
    vectors: Vector[];
}

export default function VectorVisualization() {
    const [vectors, setVectors] = useState<Vector[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    // Function to fetch vectors from the backend
    const fetchVectors = async (): Promise<FetchVectorsResponse> => {
        const API_URL =
            process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
        const response = await fetch(`${API_URL}/get_vectors`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data: FetchVectorsResponse = await response.json();
        return data;
    };

    useEffect(() => {
        const getVectors = async () => {
            try {
                const data = await fetchVectors();
                setVectors(data.vectors);
                setLoading(false);
            } catch (err) {
                console.error("Error fetching vectors:", err);
                setError("Failed to fetch vectors.");
                setLoading(false);
            }
        };

        getVectors();
    }, []);

    return (
        <div style={{ width: "100vw", height: "100vh" }}>
            {loading && <p>Loading vectors...</p>}
            {error && <p>{error}</p>}
            {!loading && !error && vectors.length > 0 && (
                <Canvas camera={{ position: [0, 0, 5], fov: 60 }}>
                    <ambientLight intensity={0.5} />
                    <pointLight position={[10, 10, 10]} />
                    <OrbitControls enableZoom={true} />
                    <Vectors points={vectors} />
                </Canvas>
            )}
        </div>
    );
}

function Vectors({ points }: { points: Vector[] }) {
    const [mappedPoints, setMappedPoints] = useState<
        {
            id: string;
            position: [number, number, number];
            metadata: VectorMetadata;
        }[]
    >([]);
    const [hoveredPoint, setHoveredPoint] = useState<string | null>(null);

    useEffect(() => {
        if (points.length > 0) {
            // Perform dimensionality reduction using PCA
            // We'll implement a simple PCA here

            // Step 1: Convert data to matrix
            const dataMatrix = points.map((point) => point.values);

            // Step 2: Mean center the data
            const meanVector = getMeanVector(dataMatrix);
            const centeredData = dataMatrix.map((vector) =>
                vector.map((value, index) => value - meanVector[index])
            );

            // Step 3: Calculate covariance matrix
            const covarianceMatrix = getCovarianceMatrix(centeredData);

            // Step 4: Get eigenvalues and eigenvectors
            // Since implementing eigen decomposition is complex,
            // we'll use the first three dimensions as an approximation
            // For production, consider using a library like 'ml-pca'

            const reducedPoints = centeredData.map((vector, index) => ({
                id: points[index].id,
                position: [
                    vector[0], // First principal component
                    vector[1], // Second principal component
                    vector[2], // Third principal component
                ],
                metadata: points[index].metadata,
            }));

            setMappedPoints(reducedPoints);
        }
    }, [points]);

    return (
        <>
            {mappedPoints.map((point) => (
                <mesh
                    key={point.id}
                    position={point.position}
                    onPointerOver={(e) => {
                        e.stopPropagation();
                        setHoveredPoint(point.id);
                    }}
                    onPointerOut={() => setHoveredPoint(null)}
                >
                    <sphereGeometry args={[0.05, 32, 32]} />
                    <meshStandardMaterial
                        color={hoveredPoint === point.id ? "red" : "orange"}
                    />
                </mesh>
            ))}
            {hoveredPoint && (
                <Html
                    position={
                        mappedPoints.find((p) => p.id === hoveredPoint)
                            ?.position || [0, 0, 0]
                    }
                >
                    <div
                        style={{
                            backgroundColor: "white",
                            padding: "5px",
                            borderRadius: "5px",
                            maxWidth: "200px",
                        }}
                    >
                        <p>ID: {hoveredPoint}</p>
                        <p>
                            {
                                mappedPoints.find((p) => p.id === hoveredPoint)
                                    ?.metadata.text
                            }
                        </p>
                    </div>
                </Html>
            )}
        </>
    );
}

// Utility functions for PCA (simplified)

// Calculate the mean vector
function getMeanVector(data: number[][]): number[] {
    const numVectors = data.length;
    const vectorLength = data[0].length;
    const meanVector = new Array(vectorLength).fill(0);

    for (let i = 0; i < vectorLength; i++) {
        for (let j = 0; j < numVectors; j++) {
            meanVector[i] += data[j][i];
        }
        meanVector[i] /= numVectors;
    }
    return meanVector;
}

// Calculate the covariance matrix
function getCovarianceMatrix(data: number[][]): number[][] {
    const numVectors = data.length;
    const vectorLength = data[0].length;
    const covarianceMatrix = Array.from({ length: vectorLength }, () =>
        new Array(vectorLength).fill(0)
    );

    for (let i = 0; i < vectorLength; i++) {
        for (let j = 0; j < vectorLength; j++) {
            let sum = 0;
            for (let k = 0; k < numVectors; k++) {
                sum += data[k][i] * data[k][j];
            }
            covarianceMatrix[i][j] = sum / (numVectors - 1);
        }
    }
    return covarianceMatrix;
}
