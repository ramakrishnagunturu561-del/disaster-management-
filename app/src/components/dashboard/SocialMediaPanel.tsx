import { MessageSquare, Twitter, Facebook, AlertTriangle, MapPin, TrendingDown, TrendingUp, Minus } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { SocialMediaReport } from '@/types';

interface SocialMediaPanelProps {
  reports: SocialMediaReport[];
}

export function SocialMediaPanel({ reports }: SocialMediaPanelProps) {
  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'twitter': return Twitter;
      case 'facebook': return Facebook;
      default: return MessageSquare;
    }
  };

  const getSentimentIcon = (sentiment: SocialMediaReport['sentiment']) => {
    switch (sentiment) {
      case 'negative': return TrendingDown;
      case 'positive': return TrendingUp;
      case 'neutral': return Minus;
    }
  };

  const getSentimentColor = (sentiment: SocialMediaReport['sentiment']) => {
    switch (sentiment) {
      case 'negative': return 'text-red-500';
      case 'positive': return 'text-green-500';
      case 'neutral': return 'text-gray-500';
    }
  };

  const formatTime = (date: Date) => {
    const diff = Date.now() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  // Calculate sentiment stats
  const sentimentStats = {
    negative: reports.filter(r => r.sentiment === 'negative').length,
    neutral: reports.filter(r => r.sentiment === 'neutral').length,
    positive: reports.filter(r => r.sentiment === 'positive').length,
  };

  const urgentReports = reports.filter(r => r.urgency);

  return (
    <Card className="border-border">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-primary" />
          Social Media Intelligence
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Sentiment Overview */}
        <div className="grid grid-cols-3 gap-2">
          <div className="text-center p-2 bg-red-500/10 rounded-lg">
            <TrendingDown className="w-4 h-4 text-red-500 mx-auto mb-1" />
            <p className="text-lg font-bold text-red-500">{sentimentStats.negative}</p>
            <p className="text-[10px] text-muted-foreground">Negative</p>
          </div>
          <div className="text-center p-2 bg-gray-500/10 rounded-lg">
            <Minus className="w-4 h-4 text-gray-500 mx-auto mb-1" />
            <p className="text-lg font-bold text-gray-500">{sentimentStats.neutral}</p>
            <p className="text-[10px] text-muted-foreground">Neutral</p>
          </div>
          <div className="text-center p-2 bg-green-500/10 rounded-lg">
            <TrendingUp className="w-4 h-4 text-green-500 mx-auto mb-1" />
            <p className="text-lg font-bold text-green-500">{sentimentStats.positive}</p>
            <p className="text-[10px] text-muted-foreground">Positive</p>
          </div>
        </div>

        {/* Urgent Reports */}
        {urgentReports.length > 0 && (
          <div className="p-3 bg-red-500/10 rounded-lg border border-red-500/30">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4 text-red-500" />
              <span className="text-sm font-medium text-red-500">
                {urgentReports.length} Urgent Distress Signals
              </span>
            </div>
            <p className="text-xs text-muted-foreground">
              AI detected urgent language patterns requiring immediate attention
            </p>
          </div>
        )}

        {/* Reports List */}
        <ScrollArea className="h-[250px]">
          <div className="space-y-3">
            {reports.map(report => {
              const PlatformIcon = getPlatformIcon(report.platform);
              const SentimentIcon = getSentimentIcon(report.sentiment);
              
              return (
                <div 
                  key={report.id} 
                  className={`p-3 rounded-lg ${
                    report.urgency ? 'bg-red-500/10 border border-red-500/30' : 'bg-muted'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <PlatformIcon className="w-4 h-4 text-muted-foreground mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-foreground">
                          {report.platform}
                        </span>
                        <SentimentIcon className={`w-3 h-3 ${getSentimentColor(report.sentiment)}`} />
                        {report.urgency && (
                          <Badge variant="outline" className="text-[10px] h-4 border-red-500 text-red-500">
                            URGENT
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-foreground mt-1 line-clamp-2">
                        {report.content}
                      </p>
                      <div className="flex items-center gap-3 mt-2">
                        {report.location && (
                          <div className="flex items-center gap-1">
                            <MapPin className="w-3 h-3 text-muted-foreground" />
                            <span className="text-[10px] text-muted-foreground">
                              {report.location[0].toFixed(3)}, {report.location[1].toFixed(3)}
                            </span>
                          </div>
                        )}
                        <span className="text-[10px] text-muted-foreground">
                          {formatTime(report.timestamp)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </ScrollArea>

        {/* Stats */}
        <div className="pt-2 border-t border-border">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Total Reports Analyzed</span>
            <span className="font-medium text-foreground">{reports.length}</span>
          </div>
          <div className="flex items-center justify-between text-xs text-muted-foreground mt-1">
            <span>Distress Signals</span>
            <span className="font-medium text-red-500">{urgentReports.length}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
