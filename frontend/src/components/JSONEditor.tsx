import React from 'react';
import Editor from '@monaco-editor/react';

interface JSONEditorProps {
    value: string;
    onChange: (value: string | undefined) => void;
    readOnly?: boolean;
    className?: string;
}

export const JSONEditor: React.FC<JSONEditorProps> = ({
    value,
    onChange,
    readOnly = false,
    className = ""
}) => {
    return (
        <div className={`h-full w-full border rounded-md overflow-hidden ${className}`}>
            <Editor
                height="100%"
                defaultLanguage="json"
                value={value}
                onChange={onChange}
                theme="vs-light"
                options={{
                    readOnly,
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    fontSize: 14,
                    wordWrap: 'on',
                    formatOnPaste: true,
                    formatOnType: true,
                    automaticLayout: true,
                }}
            />
        </div>
    );
};
