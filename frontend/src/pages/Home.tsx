import React, { useState, useRef, useEffect } from 'react';
import { JSONEditor } from '../components/JSONEditor';
import { CommentEditor } from '../components/CommentEditor';
import { Toolbar } from '../components/Toolbar';

export const Home: React.FC = () => {
    const [input, setInput] = useState<string>('{\n  "example": "json",\n  "status": "ready"\n}');
    const [comments, setComments] = useState<string>('');
    const [isValid, setIsValid] = useState<boolean | null>(null);

    // Refs for editor instances
    const jsonEditorRef = useRef<any>(null);
    const commentEditorRef = useRef<any>(null);
    const isScrollingRef = useRef<boolean>(false);

    // Helper to calculate synced comments
    const getSyncedComments = (jsonValue: string, currentComments: string) => {
        const jsonLines = jsonValue.split('\n').length;
        const commentLinesArray = currentComments.split('\n');

        if (commentLinesArray.length < jsonLines) {
            // Add missing lines
            const linesToAdd = jsonLines - commentLinesArray.length;
            return [...commentLinesArray, ...Array(linesToAdd).fill('')].join('\n');
        } else if (commentLinesArray.length > jsonLines) {
            // Trim extra empty lines at the end
            let newArray = [...commentLinesArray];
            while (newArray.length > jsonLines && newArray[newArray.length - 1].trim() === '') {
                newArray.pop();
            }
            return newArray.join('\n');
        }
        return currentComments;
    };

    // Load comments on mount
    useEffect(() => {
        fetchComments();
    }, []);

    const fetchComments = async () => {
        try {
            const response = await fetch('/api/comments');
            const data = await response.json();
            if (data.success) {
                const fetchedComments = Array.isArray(data.comments) ? data.comments.join('\n') : data.comments;
                // Sync with current input immediately
                setComments(getSyncedComments(input, fetchedComments));
            }
        } catch (error) {
            console.error('Failed to load comments:', error);
        }
    };

    // Update sync when input changes
    useEffect(() => {
        setComments(prev => getSyncedComments(input, prev));
    }, [input]);

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
                // Sync will happen via useEffect
            } else {
                setIsValid(false);
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

    const handleCopyJson = () => {
        navigator.clipboard.writeText(input);
    };

    const handleCopyAll = () => {
        const jsonLines = input.split('\n');
        const commentLines = comments.split('\n');

        const combined = jsonLines.map((line, index) => {
            const comment = commentLines[index];
            if (comment && comment.trim()) {
                return `${line} // ${comment}`;
            }
            return line;
        }).join('\n');

        navigator.clipboard.writeText(combined);
    };

    const handleClear = () => {
        setInput('');
        setComments('');
        setIsValid(null);
    };

    // Scroll Synchronization
    const handleJsonEditorMount = (editor: any) => {
        jsonEditorRef.current = editor;
        editor.onDidScrollChange((e: any) => {
            if (!isScrollingRef.current && commentEditorRef.current) {
                isScrollingRef.current = true;
                commentEditorRef.current.setScrollTop(e.scrollTop);
                isScrollingRef.current = false;
            }
        });
    };

    const handleCommentEditorMount = (editor: any) => {
        commentEditorRef.current = editor;
        editor.onDidScrollChange((e: any) => {
            if (!isScrollingRef.current && jsonEditorRef.current) {
                isScrollingRef.current = true;
                jsonEditorRef.current.setScrollTop(e.scrollTop);
                isScrollingRef.current = false;
            }
        });
    };

    return (
        <div className="flex flex-col h-screen bg-gray-50">
            <Toolbar
                onFormat={handleFormat}
                onValidate={handleValidate}
                onCopyJson={handleCopyJson}
                onCopyAll={handleCopyAll}
                onClear={handleClear}
                isValid={isValid}
            />
            <div className="flex-1 p-4 overflow-hidden flex space-x-4">
                {/* JSON Editor Pane */}
                <div className="flex-1 h-full bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
                    <div className="px-4 py-2 bg-gray-50 border-b text-sm font-medium text-gray-600">
                        JSON
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <JSONEditor
                            value={input}
                            onChange={(val) => {
                                const newVal = val || '';
                                setInput(newVal);
                                setIsValid(null);
                                // Sync comments immediately while typing
                                setComments(prev => getSyncedComments(newVal, prev));
                            }}
                            onMount={handleJsonEditorMount}
                        />
                    </div>
                </div>

                {/* Comment Editor Pane */}
                <div className="flex-1 h-full bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col">
                    <div className="px-4 py-2 bg-gray-50 border-b text-sm font-medium text-gray-600">
                        Comments
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <CommentEditor
                            value={comments}
                            onChange={(val) => setComments(val || '')}
                            onMount={handleCommentEditorMount}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};
