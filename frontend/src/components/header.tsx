"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bell, Search, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

export function Header() {
    const [mounted, setMounted] = useState(false);
    const { theme, setTheme } = useTheme();

    useEffect(() => {
        setMounted(true);
    }, []);

    return (
        <header className="bg-background border-b p-4 flex items-center justify-between">
            <div className="flex items-center">
                <Search className="h-5 w-5 text-muted-foreground mr-2" />
                <Input type="search" placeholder="Search..." className="w-64" />
            </div>
            <div className="flex items-center space-x-4">
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={() =>
                        setTheme(theme === "dark" ? "light" : "dark")
                    }
                >
                    {mounted &&
                        (theme === "dark" ? (
                            <Sun className="h-5 w-5" />
                        ) : (
                            <Moon className="h-5 w-5" />
                        ))}
                </Button>
                <Button variant="ghost" size="icon">
                    <Bell className="h-5 w-5" />
                </Button>
                <Button variant="ghost" size="sm">
                    Sign Out
                </Button>
            </div>
        </header>
    );
}
