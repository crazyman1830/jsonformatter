import React from 'react';
import Editor from '@monaco-editor/react';

interface CommentEditorProps {
    value: string;
    onChange: (value: string | undefined) => void;
    onMount?: (editor: any) => void;
    className?: string;
}

export const CommentEditor: React.FC<CommentEditorProps> = ({
    value,
    onChange,
    onMount,
    className = ""
}) => {
    return (
        <div className={`h-full w-full border rounded-md overflow-hidden bg-gray-50 ${className}`}>
            <Editor
                height="100%"
                defaultLanguage="plaintext"
                value={value}
                onChange={onChange}
                onMount={onMount}
                theme="vs-light"
                options={{
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    fontSize: 14,
                    wordWrap: 'off', // Comments usually match line-by-line
                    lineNumbers: 'on',
                    renderLineHighlight: 'all',
                    automaticLayout: true,
                    // Hide some UI elements to make it look like a side-pane
                    overviewRulerLanes: 0,
                    hideCursorInOverviewRuler: true,
                    scrollbar: {
                        vertical: 'hidden', // Hide vertical scrollbar if synced
                        horizontal: 'auto'
                    }
                }}
            />
        </div>
    );
};
