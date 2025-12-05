import React from 'react';
import { FileJson, CheckCircle, Copy, Trash2 } from 'lucide-react';

interface ToolbarProps {
    onFormat: () => void;
    onValidate: () => void;
    onCopyJson: () => void;
    onCopyAll: () => void;
    onClear: () => void;
    isValid?: boolean | null;
}

export const Toolbar: React.FC<ToolbarProps> = ({
    onFormat,
    onValidate,
    onCopyJson,
    onCopyAll,
    onClear,
    isValid
}) => {
    return (
        <div className="flex items-center justify-between p-4 bg-white border-b shadow-sm">
            <div className="flex items-center space-x-4">
                <h1 className="text-xl font-bold text-gray-800 flex items-center">
                    <FileJson className="mr-2 h-6 w-6 text-blue-600" />
                    JSON Formatter
                </h1>
                {isValid !== null && (
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${isValid
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                        }`}>
                        {isValid ? 'Valid JSON' : 'Invalid JSON'}
                    </span>
                )}
            </div>

            <div className="flex items-center space-x-2">
                <button
                    onClick={onFormat}
                    className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                    <FileJson className="mr-2 h-4 w-4" />
                    Format
                </button>
                <button
                    onClick={onValidate}
                    className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                >
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Validate
                </button>
                <button
                    onClick={onCopyJson}
                    className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                    title="Copy JSON only"
                >
                    <Copy className="mr-2 h-4 w-4" />
                    Copy JSON
                </button>
                <button
                    onClick={onCopyAll}
                    className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
                    title="Copy JSON with Comments"
                >
                    <Copy className="mr-2 h-4 w-4" />
                    Copy All
                </button>
                <button
                    onClick={onClear}
                    className="flex items-center px-4 py-2 bg-red-50 text-red-600 rounded-md hover:bg-red-100 transition-colors"
                >
                    <Trash2 className="mr-2 h-4 w-4" />
                    Clear
                </button>
            </div>
        </div>
    );
};
