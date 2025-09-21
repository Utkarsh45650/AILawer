'use client';

import React, { useEffect, useState, useId } from 'react';
import mermaid from 'mermaid';
import { Skeleton } from '@/components/ui/skeleton';

type MermaidChartProps = {
  chart: string;
};

const MermaidChart: React.FC<MermaidChartProps> = ({ chart }) => {
  const id = useId();
  const [svg, setSvg] = useState<string | null>(null);

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'base',
      securityLevel: 'loose',
      fontFamily: 'Alegreya, serif',
      themeVariables: {
        background: '#F0F4FF',
        primaryColor: '#E9EDFA',
        primaryTextColor: '#1A237E',
        primaryBorderColor: '#1A237E',
        lineColor: '#3949AB',
        secondaryColor: '#BDBDBD',
        tertiaryColor: '#fff',
      }
    });

    const renderChart = async () => {
      try {
        // The render function needs a unique ID to avoid conflicts
        const chartId = `mermaid-div-${id}`;
        const { svg: renderedSvg } = await mermaid.render(chartId, chart);
        setSvg(renderedSvg);
      } catch (error) {
        console.error('Mermaid render error:', error);
        setSvg(`<div class="p-4 text-destructive-foreground bg-destructive rounded-md">Error rendering chart. Please check the syntax.</div>`);
      }
    };
    
    if (chart) {
      // Defer rendering to next tick to ensure DOM is ready
      const timer = setTimeout(() => {
        renderChart();
      }, 0);
      return () => clearTimeout(timer);
    }
  }, [chart, id]);

  if (!svg) {
    return <Skeleton className="h-64 w-full" />;
  }

  return (
    <div 
      className="flex w-full items-center justify-center overflow-auto p-4 [&>svg]:max-w-full [&>svg]:h-auto"
      dangerouslySetInnerHTML={{ __html: svg }} 
    />
  );
};

export default MermaidChart;
