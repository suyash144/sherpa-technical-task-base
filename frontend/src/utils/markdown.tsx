import React from 'react';

interface MarkdownProps {
  content: string;
}

export function Markdown({ content }: MarkdownProps) {
  let keyCounter = 0;

  const parseInlineFormatting = (text: string): (string | JSX.Element)[] => {
    const result: (string | JSX.Element)[] = [];
    let remaining = text;
    
    while (remaining.length > 0) {
      // Find the next formatting marker
      const patterns = [
        { regex: /^```(\w*)\n?([\s\S]*?)```/, type: 'codeblock' },
        { regex: /^`([^`]+)`/, type: 'code' },
        { regex: /^\*\*([^*]+)\*\*/, type: 'bold' },
        { regex: /^__([^_]+)__/, type: 'bold' },
        { regex: /^\*([^*]+)\*/, type: 'italic' },
        { regex: /^_([^_]+)_/, type: 'italic' },
      ];

      let matched = false;
      for (const pattern of patterns) {
        const match = remaining.match(pattern.regex);
        if (match) {
          // Add the matched element
          const content = match[1] || match[2] || '';
          switch (pattern.type) {
            case 'codeblock':
              const language = match[1] || '';
              const code = match[2] || '';
              result.push(
                <pre key={`codeblock-${keyCounter++}`} className="bg-gray-800 text-green-400 p-3 rounded mt-2 mb-2 overflow-x-auto">
                  <code className={`language-${language}`}>{code}</code>
                </pre>
              );
              break;
            case 'code':
              result.push(
                <code key={`code-${keyCounter++}`} className="bg-gray-200 px-1 rounded text-sm font-mono">
                  {content}
                </code>
              );
              break;
            case 'bold':
              result.push(
                <strong key={`bold-${keyCounter++}`}>
                  {content}
                </strong>
              );
              break;
            case 'italic':
              result.push(
                <em key={`italic-${keyCounter++}`}>
                  {content}
                </em>
              );
              break;
          }
          remaining = remaining.slice(match[0].length);
          matched = true;
          break;
        }
      }

      if (!matched) {
        // No formatting found, add the next character and continue
        result.push(remaining[0]);
        remaining = remaining.slice(1);
      }
    }

    return result;
  };

  const processLine = (line: string): JSX.Element | string => {
    // Handle headers
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
      return (
        <HeaderTag key={`header-${keyCounter++}`} className={headerClasses[level as keyof typeof headerClasses]}>
          {parseInlineFormatting(headerText)}
        </HeaderTag>
      );
    }

    // Handle unordered lists
    const listMatch = line.match(/^\s*[-*+]\s(.*)$/);
    if (listMatch) {
      const listContent = listMatch[1];
      return (
        <div key={`list-${keyCounter++}`} className="flex items-start ml-4">
          <span className="mr-2">•</span>
          <span>{parseInlineFormatting(listContent)}</span>
        </div>
      );
    }

    // Handle numbered lists
    const numberedListMatch = line.match(/^\s*(\d+)\.\s(.*)$/);
    if (numberedListMatch) {
      const number = numberedListMatch[1];
      const listContent = numberedListMatch[2];
      return (
        <div key={`numlist-${keyCounter++}`} className="flex items-start ml-4">
          <span className="mr-2">{number}.</span>
          <span>{parseInlineFormatting(listContent)}</span>
        </div>
      );
    }

    // Handle code blocks
    if (line.startsWith('```')) {
      return line; // Will be handled by the main processing
    }

    // Regular line
    if (line.trim()) {
      return (
        <div key={`line-${keyCounter++}`}>
          {parseInlineFormatting(line)}
        </div>
      );
    }

    return '';
  };

  const processText = (text: string): (JSX.Element | string)[] => {
    const result: (JSX.Element | string)[] = [];
    const lines = text.split('\n');
    let i = 0;

    while (i < lines.length) {
      const line = lines[i];

      // Handle code blocks
      if (line.startsWith('```')) {
        const language = line.slice(3).trim();
        let codeContent = '';
        i++; // Move to next line
        
        // Collect code content until closing ```
        while (i < lines.length && !lines[i].startsWith('```')) {
          codeContent += lines[i] + '\n';
          i++;
        }
        
        result.push(
          <pre key={`codeblock-${keyCounter++}`} className="bg-gray-800 text-green-400 p-3 rounded mt-2 mb-2 overflow-x-auto">
            <code className={`language-${language}`}>{codeContent.trim()}</code>
          </pre>
        );
        i++; // Skip closing ```
        continue;
      }

      // Process regular line
      const processedLine = processLine(line);
      if (processedLine) {
        result.push(processedLine);
      } else if (line.trim() === '') {
        // Add line break for empty lines
        result.push(<br key={`br-${keyCounter++}`} />);
      }

      i++;
    }

    return result;
  };

  return (
    <div className="markdown-content space-y-1">
      {processText(content)}
    </div>
  );
} 