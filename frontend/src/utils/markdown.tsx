import React from 'react';

interface MarkdownProps {
  content: string;
}

export function Markdown({ content }: MarkdownProps) {
  const renderMarkdown = (text: string) => {
    // Split by code blocks first to preserve them
    const codeBlockRegex = /```(\w*)\n?([\s\S]*?)```/g;
    const parts: (string | JSX.Element)[] = [];
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(text)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        const beforeText = text.slice(lastIndex, match.index);
        parts.push(...renderInlineMarkdown(beforeText));
      }

      // Add code block
      const language = match[1] || '';
      const code = match[2];
      parts.push(
        <pre key={match.index} className="bg-gray-800 text-green-400 p-3 rounded mt-2 mb-2 overflow-x-auto">
          <code className={`language-${language}`}>{code}</code>
        </pre>
      );

      lastIndex = match.index + match[0].length;
    }

    // Add remaining text
    if (lastIndex < text.length) {
      const remainingText = text.slice(lastIndex);
      parts.push(...renderInlineMarkdown(remainingText));
    }

    return parts;
  };

  const renderInlineMarkdown = (text: string): (string | JSX.Element)[] => {
    const parts: (string | JSX.Element)[] = [];
    let currentText = text;
    let keyCounter = 0;

    // Handle line breaks
    const lines = currentText.split('\n');
    for (let i = 0; i < lines.length; i++) {
      if (i > 0) {
        parts.push(<br key={`br-${keyCounter++}`} />);
      }

      let line = lines[i];

      // Handle lists
      if (line.match(/^\s*[-*+]\s/)) {
        const listContent = line.replace(/^\s*[-*+]\s/, '');
        parts.push(
          <div key={`list-${keyCounter++}`} className="flex items-start">
            <span className="mr-2">•</span>
            <span>{processInlineFormatting(listContent, keyCounter++)}</span>
          </div>
        );
        continue;
      }

      // Handle numbered lists
      if (line.match(/^\s*\d+\.\s/)) {
        const listMatch = line.match(/^\s*(\d+)\.\s(.*)$/);
        if (listMatch) {
          const number = listMatch[1];
          const listContent = listMatch[2];
          parts.push(
            <div key={`numlist-${keyCounter++}`} className="flex items-start">
              <span className="mr-2">{number}.</span>
              <span>{processInlineFormatting(listContent, keyCounter++)}</span>
            </div>
          );
          continue;
        }
      }

      // Handle headers
      if (line.match(/^#{1,6}\s/)) {
        const headerMatch = line.match(/^(#{1,6})\s(.*)$/);
        if (headerMatch) {
          const level = headerMatch[1].length;
          const headerText = headerMatch[2];
          const HeaderTag = `h${level}` as keyof JSX.IntrinsicElements;
          const headerClasses = {
            1: 'text-2xl font-bold mt-4 mb-2',
            2: 'text-xl font-bold mt-3 mb-2',
            3: 'text-lg font-bold mt-2 mb-1',
            4: 'text-base font-bold mt-2 mb-1',
            5: 'text-sm font-bold mt-1 mb-1',
            6: 'text-xs font-bold mt-1 mb-1'
          };
          parts.push(
            <HeaderTag key={`header-${keyCounter++}`} className={headerClasses[level as keyof typeof headerClasses]}>
              {processInlineFormatting(headerText, keyCounter++)}
            </HeaderTag>
          );
          continue;
        }
      }

      // Regular text with inline formatting
      if (line.trim()) {
        parts.push(
          <span key={`text-${keyCounter++}`}>
            {processInlineFormatting(line, keyCounter++)}
          </span>
        );
      }
    }

    return parts;
  };

  const processInlineFormatting = (text: string, baseKey: number): (string | JSX.Element)[] => {
    const parts: (string | JSX.Element)[] = [];
    let currentText = text;
    let keyCounter = baseKey;

    // Handle inline code first (to preserve it from other formatting)
    const inlineCodeRegex = /`([^`]+)`/g;
    const codeMatches: Array<{ match: RegExpExecArray; replacement: JSX.Element }> = [];
    let match;

    while ((match = inlineCodeRegex.exec(text)) !== null) {
      const codeElement = (
        <code key={`code-${keyCounter++}`} className="bg-gray-200 px-1 rounded text-sm font-mono">
          {match[1]}
        </code>
      );
      codeMatches.push({ match, replacement: codeElement });
    }

    // Replace from end to start to maintain indices
    codeMatches.reverse().forEach(({ match, replacement }) => {
      const before = currentText.slice(0, match.index);
      const after = currentText.slice(match.index! + match[0].length);
      
      // Process formatting in the parts before and after
      const afterParts = after ? processOtherFormatting(after, keyCounter++) : [];
      const beforeParts = before ? processOtherFormatting(before, keyCounter++) : [];
      
      parts.unshift(...afterParts);
      parts.unshift(replacement);
      parts.unshift(...beforeParts);
      
      currentText = currentText.slice(0, match.index);
    });

    // If no inline code was found, process other formatting
    if (codeMatches.length === 0) {
      parts.push(...processOtherFormatting(currentText, keyCounter));
    }

    return parts;
  };

  const processOtherFormatting = (text: string, baseKey: number): (string | JSX.Element)[] => {
    // Handle bold, italic, etc.
    let result = text;
    const elements: JSX.Element[] = [];
    let keyCounter = baseKey;

    // Bold (**text** or __text__)
    result = result.replace(/\*\*(.*?)\*\*/g, (_, content) => {
      const key = `bold-${keyCounter++}`;
      elements.push(<strong key={key}>{content}</strong>);
      return `__ELEMENT_${key}__`;
    });

    result = result.replace(/__(.*?)__/g, (_, content) => {
      const key = `bold-${keyCounter++}`;
      elements.push(<strong key={key}>{content}</strong>);
      return `__ELEMENT_${key}__`;
    });

    // Italic (*text* or _text_)
    result = result.replace(/\*(.*?)\*/g, (_, content) => {
      const key = `italic-${keyCounter++}`;
      elements.push(<em key={key}>{content}</em>);
      return `__ELEMENT_${key}__`;
    });

    result = result.replace(/_(.*?)_/g, (_, content) => {
      const key = `italic-${keyCounter++}`;
      elements.push(<em key={key}>{content}</em>);
      return `__ELEMENT_${key}__`;
    });

    // Replace placeholders with actual elements
    const parts: (string | JSX.Element)[] = [];
    const elementRegex = /__ELEMENT_(.*?)__/g;
    let lastIndex = 0;
    let elementMatch;

    while ((elementMatch = elementRegex.exec(result)) !== null) {
      // Add text before element
      if (elementMatch.index > lastIndex) {
        const textBefore = result.slice(lastIndex, elementMatch.index);
        if (textBefore) parts.push(textBefore);
      }

      // Add element
      const elementKey = elementMatch[1];
      const element = elements.find(el => el.key === elementKey);
      if (element) parts.push(element);

      lastIndex = elementMatch.index + elementMatch[0].length;
    }

    // Add remaining text
    if (lastIndex < result.length) {
      const remainingText = result.slice(lastIndex);
      if (remainingText) parts.push(remainingText);
    }

    // If no elements were replaced, return the original text
    if (parts.length === 0) {
      return [text];
    }

    return parts;
  };

  return <div className="markdown-content">{renderMarkdown(content)}</div>;
} 