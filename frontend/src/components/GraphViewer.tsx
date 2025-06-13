
import { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { Button } from '@/components/ui/button';
import { RotateCcw, Loader2 } from 'lucide-react';

interface Node {
  id: string;
  type: string;
  description?: string;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

interface Edge {
  id: string;
  source: string | Node;
  target: string | Node;
  relationship: string;
  description?: string;
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

interface GraphViewerProps {
  data: GraphData;
  onReset: () => void;
  isLoading: boolean;
  highlightedNodes?: string[];
}

const GraphViewer: React.FC<GraphViewerProps> = ({ data, onReset, isLoading, highlightedNodes = [] }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const simulationRef = useRef<d3.Simulation<Node, Edge> | null>(null);

  useEffect(() => {
    if (!svgRef.current || !data.nodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    // Create zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
      });

    svg.call(zoom);

    const container = svg.append('g');

    const initialZoomScale = 0.8;
    const initialTranslate = [width * 0.1, height * 0.1];

    container.attr('transform', `translate(${initialTranslate}) scale(${initialZoomScale})`);


    // Color scale for different node types
    const colorScale = d3.scaleOrdinal<string>()
      .domain(['topic', 'concept', 'field', 'document', 'entity'])
      .range(['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444']);

    // Create simulation
    const simulation = d3.forceSimulation<Node>(data.nodes)
      .force('link', d3.forceLink<Node, Edge>(data.edges).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-100))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));

    simulationRef.current = simulation;

    // Create tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'absolute bg-popover text-popover-foreground p-2 rounded border shadow-lg pointer-events-none opacity-0 transition-opacity z-50')
      .style('max-width', '200px');

    // Create edges
    const links = container.append('g')
      .selectAll('line')
      .data(data.edges)
      .enter().append('line')
      .attr('stroke', '#6b7280')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.6);

    // Create edge labels
    const linkLabels = container.append('g')
      .selectAll('text')
      .data(data.edges)
      .enter().append('text')
      .attr('font-size', '10px')
      .attr('fill', '#6b7280')
      .attr('text-anchor', 'middle')
      .text(d => d.relationship);

    // Create nodes with highlighting
    const nodes = container.append('g')
      .selectAll('circle')
      .data(data.nodes)
      .enter().append('circle')
      .attr('r', d => highlightedNodes.includes(d.id) ? 25 : 20)
      .attr('fill', d => colorScale(d.type))
      .attr('stroke', d => highlightedNodes.includes(d.id) ? '#fbbf24' : '#ffffff')
      .attr('stroke-width', d => highlightedNodes.includes(d.id) ? 3 : 2)
      .style('cursor', 'pointer')
      .style('filter', d => highlightedNodes.includes(d.id) ? 'drop-shadow(0 0 8px rgba(251, 191, 36, 0.6))' : 'none')
      .call(d3.drag<SVGCircleElement, Node>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null;
          d.fy = null;
        }));

    // Create node labels
    const labels = container.append('g')
      .selectAll('text')
      .data(data.nodes)
      .enter().append('text')
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .attr('fill', '#374151')
      .attr('text-anchor', 'middle')
      .attr('dy', '.35em')
      .text(d => d.id)
      .style('pointer-events', 'none');

    // Add hover effects
    nodes
      .on('mouseenter', (event, d) => {
        d3.select(event.currentTarget)
          .transition()
          .duration(200)
          .attr('r', 25);
        
        tooltip
          .style('opacity', 1)
          .html(`<strong>${d.id}</strong><br/>${d.type}<br/>${d.description || 'No description'}`)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseleave', (event) => {
        d3.select(event.currentTarget)
          .transition()
          .duration(200)
          .attr('r', 20);
        
        tooltip.style('opacity', 0);
      });

      links
      .on('mouseenter', (event, d) => {
        d3.select(event.currentTarget)
          .transition()
          .duration(200)
          .attr('r', 25);
        
        tooltip
          .style('opacity', 1)
          .html(`<strong>${d.relationship}</strong><br/>${d.description || 'No description'}`)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 10) + 'px');
      })
      .on('mouseleave', (event) => {
        d3.select(event.currentTarget)
          .transition()
          .duration(200)
          .attr('r', 20);
        
        tooltip.style('opacity', 0);
      });

    // Update positions on simulation tick
    simulation.on('tick', () => {
      links
        .attr('x1', d => (d.source as Node).x!)
        .attr('y1', d => (d.source as Node).y!)
        .attr('x2', d => (d.target as Node).x!)
        .attr('y2', d => (d.target as Node).y!);

      linkLabels
        .attr('x', d => ((d.source as Node).x! + (d.target as Node).x!) / 2)
        .attr('y', d => ((d.source as Node).y! + (d.target as Node).y!) / 2);

      nodes
        .attr('cx', d => d.x!)
        .attr('cy', d => d.y!);

      labels
        .attr('x', d => d.x!)
        .attr('y', d => d.y!);
    });

    return () => {
      tooltip.remove();
      if (simulationRef.current) {
        simulationRef.current.stop();
      }
    };
  }, [data, highlightedNodes]);

  return (
    <div className="h-full flex flex-col">
      {/* Compact header */}
      <div className="p-3 border-b bg-muted/30">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-medium">Graph</h2>
            <p className="text-xs text-muted-foreground">
              {data.nodes.length} nodes, {data.edges.length} edges
            </p>
          </div>
          <Button
            onClick={onReset}
            variant="ghost"
            size="sm"
            disabled={isLoading}
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RotateCcw className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
      
      <div className="flex-1 relative overflow-hidden">
        {data.nodes.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <div className="text-3xl mb-3">🕸️</div>
              <p className="text-sm font-medium">No graph data</p>
              <p className="text-xs">Upload a document to start</p>
            </div>
          </div>
        ) : (
          <svg
            ref={svgRef}
            className="w-full h-full"
            style={{ background: 'radial-gradient(circle, #f8fafc 0%, #f1f5f9 100%)' }}
          />
        )}
      </div>
    </div>
  );
};

export default GraphViewer;
