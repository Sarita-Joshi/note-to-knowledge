
import { CheckCircle, Plus, Link, Clock, FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

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

interface UploadSummaryProps {
  changes: UploadChange | null;
  isVisible: boolean;
  onClose: () => void;
}

const UploadSummary: React.FC<UploadSummaryProps> = ({ changes, isVisible, onClose }) => {
  if (!isVisible || !changes) return null;

  return (
    <Card className="mb-4 border-green-200 bg-green-50">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-green-800">
          <CheckCircle className="h-5 w-5" />
          Document Processed Successfully
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="text-sm text-muted-foreground">
          <FileText className="h-4 w-4 inline mr-1" />
          {changes.documentTitle}
        </div>
        
        {changes.newEntities.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Plus className="h-4 w-4 text-blue-600" />
              <span className="font-medium text-sm">
                {changes.newEntities.length} new entities added:
              </span>
            </div>
            <div className="flex flex-wrap gap-1">
              {changes.newEntities.slice(0,5).map((entity, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {entity}
                </Badge>
              ))}
              {changes.newEntities.length > 5 && (
                <div className="text-xs text-muted-foreground italic">
                  +{changes.newEntities.length - 5} more...
                </div>
              )}
            </div>
          </div>
        )}

        {changes.newRelationships.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Link className="h-4 w-4 text-green-600" />
              <span className="font-medium text-sm">
                {changes.newRelationships.length} new relationships formed:
              </span>
            </div>
            <div className="space-y-1">
              {changes.newRelationships.slice(0, 3).map((rel, index) => (
                <div key={index} className="text-xs text-muted-foreground">
                  "{rel.source}" → {rel.relationship} → "{rel.target}"
                </div>
              ))}
              {changes.newRelationships.length > 3 && (
                <div className="text-xs text-muted-foreground italic">
                  +{changes.newRelationships.length - 3} more...
                </div>
              )}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            {changes.timestamp.toLocaleTimeString()}
          </div>
          <button
            onClick={onClose}
            className="text-xs text-green-700 hover:text-green-800"
          >
            Dismiss
          </button>
        </div>
      </CardContent>
    </Card>
  );
};

export default UploadSummary;
