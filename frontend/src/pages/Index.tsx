import { useState, useEffect } from 'react';
import GraphViewer from '../components/GraphViewer';
import ChatInterface from '../components/ChatInterface';
import UploadSummary from '../components/UploadSummary';
import { UploadRecord } from '../components/UploadHistory';
import { toast } from '@/hooks/use-toast';
import { Drawer, DrawerContent, DrawerTrigger } from '@/components/ui/drawer';
import { Button } from '@/components/ui/button';
import { BarChart3 } from 'lucide-react';

interface GraphData {
  nodes: Array<{
    id: string;
    type: string;
    description?: string;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    relationship: string;
    description?: string;
  }>;
}

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface UploadChange {
  newEntities: string[];
  newRelationships: Array<{
    source: string;
    target: string;
    relationship: string;
  }>;
  timestamp: Date;
  documentTitle: string;
}

const Index = () => {
  const [graphId, setGraphId] = useState<string | null>(() => {
    return localStorage.getItem("graphId");
  });

  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [newGraphChanges, setNewGraphChanges] = useState<GraphData>({ nodes: [], edges: [] });
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadHistory, setUploadHistory] = useState<UploadRecord[]>([]);
  const [lastUploadChanges, setLastUploadChanges] = useState<UploadChange | null>(null);
  const [showUploadSummary, setShowUploadSummary] = useState(false);
  const [highlightedNodes, setHighlightedNodes] = useState<string[]>([]);

  // Simulate initial graph data for demo
  useEffect(() => {
    const sampleData: GraphData = {
      nodes: [
        { id:  'AI Research', type: 'topic', description: 'Artificial Intelligence research and development' },
        { id: 'Machine Learning', type: 'topic', description: 'ML algorithms and techniques' },
        { id: 'Neural Networks', type: 'concept', description: 'Deep learning neural network architectures' },
        { id: 'Data Science', type: 'field', description: 'Data analysis and scientific computing' }
      ],
      edges: [
        { id:'e1',  source: 'AI Research', target: 'Machine Learning', relationship: 'includes' },
        { id:'e2', source: 'Machine Learning', target: 'Neural Networks', relationship: 'uses' },
        { id:'e3', source: 'Machine Learning', target: 'Data Science', relationship: 'overlaps' }
      ]
    };
    setGraphData(sampleData);
  }, []);

  useEffect(() => {
    if (graphId) {
      localStorage.setItem("graphId", graphId);
    }
  }, [graphId]);

  const handleSendMessage = async (message: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      text: message,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      
      const chatResponse = await fetch(`http://localhost:8000/chat?question=${message}&graph_id=${graphId}`, {
        method: "GET",
      });
      const result = await chatResponse.text(); // plain text
      var sample = `Based on your knowledge graph, I can see connections between ${graphData.nodes.length} entities. Your question about "${message}" relates to the current graph structure. This is a simulated response - connect to your GraphRAG backend to get real insights!`
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: result || sample,
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDocumentUpload = async (text: string) => {
  setIsLoading(true);

  try {

    const formData = new FormData();
      formData.append("text", text);
      if (graphId) {
        formData.append("graph_id", graphId);
      }
      
      // Step 1: Upload text to backend
      const uploadResponse = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await uploadResponse.json();
      if (!uploadResponse.ok) throw new Error(data.detail || "Upload failed");
      //Get graph data and graphId from response
      const { graph, graph_id } = data;
      console.log(graph_id);
      console.log(graph);
      setGraphId(graph_id);

      const formattedNodes = graph.nodes.map((node: any) => ({
        id: node.id,
        type: node.type,
        description: node.description,
      }));

      const formattedEdges = graph.edges.map((edge: any, index: number) => ({
        id: `${edge.source}_${edge.target}_${index}`,
        source: edge.source,
        target: edge.target,
        relationship: edge.relationship,
        description: edge.description,
      }));

      // Step 3: Compare with existing graph to find new entries
      const existingNodeIds = new Set(graphData.nodes.map(n => n.id));
      const existingEdgeIds = new Set(graphData.edges.map(e => e.id));

      const newNodes = formattedNodes.filter(n => !existingNodeIds.has(n.id));
      const newEdges = formattedEdges.filter(e => !existingEdgeIds.has(e.id));

      // Step 4: Update graph (replace the entire sample with real graph)
      setGraphData({
        nodes: formattedNodes,
        edges: formattedEdges,
      });

      // Step 5: Track changes
      const documentTitle = `Document ${Date.now()}`;
      const changes: UploadChange = {
        newEntities: newNodes.map(n => n.id),
        newRelationships: newEdges.map(e => ({
          source: e.source,
          target: e.target,
          relationship: e.relationship,
        })),
        timestamp: new Date(),
        documentTitle,
      };

      const uploadRecord: UploadRecord = {
        id: Date.now().toString(),
        documentTitle,
        timestamp: new Date(),
        newEntities: changes.newEntities,
        newRelationships: changes.newRelationships,
        documentPreview: text.substring(0, 100),
      };

      setUploadHistory(prev => [uploadRecord, ...prev]);
      setLastUploadChanges(changes);
      setShowUploadSummary(true);
      setHighlightedNodes(newNodes.map(n => n.id));
      setTimeout(() => setHighlightedNodes([]), 3000);

      // Optional: track raw changes if you want to reuse later
      setNewGraphChanges({
        nodes: newNodes,
        edges: newEdges,
      });

      toast({
        title: "Document Uploaded",
        description: `Processed successfully! Added ${changes.newEntities.length} entities and ${changes.newRelationships.length} relationships.`,
      });
    } catch (error: any) {
      toast({
        title: "Upload Error",
        description: error.message || "Failed to process document. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReloadGraph = async () => {
      const uploadResponse = await fetch(`http://localhost:8000/graph?graph_id=${graphId}`, {
        method: "GET"
      });

      const graph = await uploadResponse.json();
      if (!uploadResponse.ok) throw new Error(graph.detail || "Reload failed");
      //Get graph data and graphId from response
    
      const formattedNodes = graph.nodes.map((node: any) => ({
        id: node.id,
        type: node.type,
        description: node.description,
      }));

      const formattedEdges = graph.edges.map((edge: any, index: number) => ({
        id: `${edge.source}_${edge.target}_${index}`,
        source: edge.source,
        target: edge.target,
        relationship: edge.relationship,
        description: edge.description,
      }));

      // Step 4: Update graph (replace the entire sample with real graph)
      setGraphData({
        nodes: formattedNodes,
        edges: formattedEdges,
      });
    toast({
      title: "Graph Reload",
      description: "Graph data has been restored.",
    });
  };

  const handleClearConversation = () => {
    setMessages([]);
    toast({
      title: "Conversation Cleared",
      description: "Chat history has been cleared.",
    });
  };

  const handleResetAll = () => {
    setGraphData({ nodes: [], edges: [] });
    setGraphId(null);
    setMessages([]);
    setUploadHistory([]);
    setLastUploadChanges(null);
    setShowUploadSummary(false);
    setHighlightedNodes([]);
    toast({
      title: "All Data Reset",
      description: "Graph, conversation, and upload history have been cleared.",
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-2 sm:p-3 h-screen flex flex-col">
        {/* Minimal header */}
        <header className="mb-2 sm:mb-4">
          <h1 className="text-lg sm:text-xl font-bold mb-1">Knowledge Graph Explorer</h1>
        </header>

        {/* Desktop Layout */}
        <div className="hidden lg:flex flex-1 gap-4 min-h-0">
          {/* Graph area - prominent */}
          <div className="flex-[2.5] bg-card rounded-lg border shadow-sm overflow-hidden">
            <GraphViewer 
              data={graphData} 
              onReset={handleReloadGraph}
              isLoading={isLoading}
              highlightedNodes={highlightedNodes}
            />
          </div>

          {/* Chat area - compact */}
          <div className="flex-1 max-w-sm bg-card rounded-lg border shadow-sm overflow-hidden flex flex-col">
            <UploadSummary
              changes={lastUploadChanges}
              isVisible={showUploadSummary}
              onClose={() => setShowUploadSummary(false)}
            />
            <div className="flex-1">
              <ChatInterface
                messages={messages}
                onSendMessage={handleSendMessage}
                onDocumentUpload={handleDocumentUpload}
                onClearConversation={handleClearConversation}
                onResetAll={handleResetAll}
                isLoading={isLoading}
                uploadHistory={uploadHistory}
              />
            </div>
          </div>
        </div>

        {/* Mobile Layout */}
        <div className="lg:hidden flex flex-col flex-1 min-h-0">
          {/* Chat takes full mobile screen */}
          <div className="flex-1 bg-card rounded-lg border shadow-sm overflow-hidden flex flex-col">
            <UploadSummary
              changes={lastUploadChanges}
              isVisible={showUploadSummary}
              onClose={() => setShowUploadSummary(false)}
            />
            <div className="flex-1">
              <ChatInterface
                messages={messages}
                onSendMessage={handleSendMessage}
                onDocumentUpload={handleDocumentUpload}
                onClearConversation={handleClearConversation}
                onResetAll={handleResetAll}
                isLoading={isLoading}
                uploadHistory={uploadHistory}
              />
            </div>
          </div>

          {/* Mobile Graph Drawer */}
          <Drawer>
            <DrawerTrigger asChild>
              <Button 
                className="fixed bottom-4 right-4 h-12 w-12 rounded-full shadow-lg z-50" 
                size="icon"
              >
                <BarChart3 className="h-5 w-5" />
              </Button>
            </DrawerTrigger>
            <DrawerContent className="h-[80vh]">
              <div className="h-full p-2">
                <GraphViewer 
                  data={graphData} 
                  onReset={handleReloadGraph}
                  isLoading={isLoading}
                  highlightedNodes={highlightedNodes}
                />
              </div>
            </DrawerContent>
          </Drawer>
        </div>
      </div>
    </div>
  );
};

export default Index;
