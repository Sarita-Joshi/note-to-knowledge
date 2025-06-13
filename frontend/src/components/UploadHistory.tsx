
import { useState } from 'react';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { History, FileText, Plus, Link, Clock } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export interface UploadRecord {
  id: string;
  documentTitle: string;
  timestamp: Date;
  newEntities: string[];
  newRelationships: Array<{
    source: string;
    target: string;
    relationship: string;
  }>;
  documentPreview: string;
}

interface UploadHistoryProps {
  uploadHistory: UploadRecord[];
}

const UploadHistory: React.FC<UploadHistoryProps> = ({ uploadHistory }) => {
  const [isOpen, setIsOpen] = useState(false);

  const formatDate = (date: Date) => {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <Sheet open={isOpen} onOpenChange={setIsOpen}>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm">
          <History className="h-4 w-4" />
          Upload History ({uploadHistory.length})
        </Button>
      </SheetTrigger>
      <SheetContent className="w-[400px] sm:w-[540px]">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Upload History
          </SheetTitle>
        </SheetHeader>
        
        <ScrollArea className="h-[calc(100vh-100px)] mt-4">
          {uploadHistory.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No uploads yet</p>
              <p className="text-sm">Upload a document to see it here</p>
            </div>
          ) : (
            <div className="space-y-4">
              {uploadHistory.map((record) => (
                <div key={record.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium text-sm">{record.documentTitle}</h4>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                        <Clock className="h-3 w-3" />
                        {formatDate(record.timestamp)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-xs text-muted-foreground bg-muted p-2 rounded">
                    {record.documentPreview}...
                  </div>

                  <div className="space-y-2">
                    {record.newEntities.length > 0 && (
                      <div>
                        <div className="flex items-center gap-1 text-xs font-medium">
                          <Plus className="h-3 w-3 text-blue-600" />
                          {record.newEntities.length} entities
                        </div>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {record.newEntities.slice(0, 3).map((entity, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {entity}
                            </Badge>
                          ))}
                          {record.newEntities.length > 3 && (
                            <span className="text-xs text-muted-foreground">
                              +{record.newEntities.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {record.newRelationships.length > 0 && (
                      <div>
                        <div className="flex items-center gap-1 text-xs font-medium">
                          <Link className="h-3 w-3 text-green-600" />
                          {record.newRelationships.length} relationships
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
};

export default UploadHistory;
