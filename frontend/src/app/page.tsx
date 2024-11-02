import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Home() {
    return (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
                <CardHeader>
                    <CardTitle>Total Documents</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-3xl font-bold"></p>
                </CardContent>
            </Card>
            <Card>
                <CardHeader>
                    <CardTitle>Questions Asked</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-3xl font-bold"></p>
                </CardContent>
            </Card>
            <Card>
                <CardHeader>
                    <CardTitle>Accuracy Rate</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-3xl font-bold"></p>
                </CardContent>
            </Card>
        </div>
    );
}
