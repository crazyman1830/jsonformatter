import React, { useState } from 'react';
import { JSONEditor } from '../components/JSONEditor';
import { Toolbar } from '../components/Toolbar';

export const Home: React.FC = () => {
    const [input, setInput] = useState<string>('{\n  "example": "json",\n  "status": "ready"\n}');
    const [isValid, setIsValid] = useState<boolean | null>(null);

    const handleFormat = async () => {
        if (!input.trim()) return;

        try {
            const response = await fetch('/api/format', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ json_data: input, indent: 2, sort_keys: true }),
            });
            const data = await response.json();

            if (data.success) {
                setInput(data.formatted_json);
                setIsValid(true);
            } else {
                setIsValid(false);
                // Ideally show a toast notification here
                console.error(data.error_message);
            }
        } catch (error) {
            console.error('Format error:', error);
            alert('Failed to format JSON. Check console for details.');
        }
    };

    const handleValidate = async () => {
        if (!input.trim()) return;

        try {
            const response = await fetch('/api/validate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ json_data: input }),
            });
            const data = await response.json();

            setIsValid(data.is_valid);
            if (!data.is_valid) {
                console.error(data.error_message);
            }
        } catch (error) {
            console.error('Validation error:', error);
            alert('Failed to validate JSON');
        }
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(input);
        // Toast notification would be better
    };

    const handleClear = () => {
        setInput('');
        setIsValid(null);
    };

    return (
        <div className="flex flex-col h-screen bg-gray-50">
            <Toolbar
                onFormat={handleFormat}
                onValidate={handleValidate}
                onCopy={handleCopy}
                onClear={handleClear}
                isValid={isValid}
            />
            <div className="flex-1 p-4 overflow-hidden">
                <div className="h-full bg-white rounded-lg shadow-sm border border-gray-200">
                    <JSONEditor
                        value={input}
                        onChange={(val) => {
                            setInput(val || '');
                            setIsValid(null); // Reset validation on change
                        }}
                    />
                </div>
            </div>
        </div>
    );
};
