// lib/api.ts

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// Define interfaces for type safety
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

export const fetchAnalysis = async () => {
    const response = await fetch(`${API_URL}/analysis`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "include", // Remove if not using cookies
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
};

export const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_URL}/upload_pdf`, {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
};

export const askQuestion = async (question: string) => {
    const response = await fetch(`${API_URL}/ask_question`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json(); // Returns { answer: "..." }
};

// Add the fetchVectors function here
export const fetchVectors = async (): Promise<FetchVectorsResponse> => {
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
