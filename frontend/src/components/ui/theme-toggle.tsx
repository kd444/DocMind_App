"use client";

import { Button } from "@/components/ui/button";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export default function Component() {
    const [mounted, setMounted] = useState(false);
    const { theme, setTheme } = useTheme();

    // Only render theme switcher after mounting to avoid hydration mismatch
    useEffect(() => {
        setMounted(true);
    }, []);

    // Don't render anything until mounted to prevent hydration mismatch
    if (!mounted) {
        return null;
    }

    return (
        <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            aria-label={
                theme === "dark"
                    ? "Switch to light theme"
                    : "Switch to dark theme"
            }
        >
            {/* Only render the correct icon after mounting */}
            {theme === "dark" ? (
                <Sun className="h-5 w-5" />
            ) : (
                <Moon className="h-5 w-5" />
            )}
        </Button>
    );
}
