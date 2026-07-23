import { useState } from 'react';
import { 
  LayoutDashboard, Map, BarChart3, Activity, 
  Settings, HelpCircle, Menu, X, Shield, Satellite, Radio, AlertTriangle,
  Bot, ShieldCheck
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { useDashboardData } from '@/hooks/useDashboardData';
import { useDamageDetection } from '@/hooks/useDamageDetection';
import { Header } from '@/components/dashboard/Header';
import { ResourceStatusBar } from '@/components/dashboard/ResourceStatusBar';
import { DisasterMap } from '@/components/dashboard/DisasterMap';
import { RiskAssessmentPanel } from '@/components/dashboard/RiskAssessmentPanel';
import { RecommendationsPanel } from '@/components/dashboard/RecommendationsPanel';
import { EmergencyTimeline } from '@/components/dashboard/EmergencyTimeline';
import { DamageDetectionPanel } from '@/components/dashboard/DamageDetectionPanel';
import { SensorDataPanel } from '@/components/dashboard/SensorDataPanel';
import { SocialMediaPanel } from '@/components/dashboard/SocialMediaPanel';
import { AgentOperationsPanel } from '@/components/dashboard/AgentOperationsPanel';
import { DecisionApprovalCenter } from '@/components/dashboard/DecisionApprovalCenter';
import { api } from '@/services/api';
import './App.css';

type ViewType = 'dashboard' | 'agents' | 'approval' | 'map' | 'analytics' | 'livefeed';

function App() {
  const [selectedZone, setSelectedZone] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentView, setCurrentView] = useState<ViewType>('dashboard');

  // Multi-Agent State
  const [agentState, setAgentState] = useState<Record<string, unknown> | null>(null);
  const [isAgentRunning, setIsAgentRunning] = useState(false);
  
  const {
    zones,
    resources,
    recommendations,
    timelineEvents,
    sensorData,
    socialReports,
    incident,
    isSimulating,
    startSimulation,
    stopSimulation,
    executeRecommendation,
    dismissRecommendation,
  } = useDashboardData();

  const {
    detections,
    currentDetection,
    isAnalyzing,
    uploadAndAnalyze,
    selectDetection,
    clearDetections,
  } = useDamageDetection();

  const toggleSimulation = () => {
    if (isSimulating) {
      stopSimulation();
    } else {
      startSimulation();
    }
  };

  const handleRunAgentWorkflow = async () => {
    setIsAgentRunning(true);
    try {
      const incId = incident?.id || 'inc-vijayawada-01';
      const stateData = await api.runAgentWorkflow(incId);
      setAgentState(stateData);
    } catch (err) {
      console.error('Workflow trigger failed:', err);
    } finally {
      setIsAgentRunning(false);
    }
  };

  const handleApprovePlan = async () => {
    try {
      const incId = incident?.id || 'inc-vijayawada-01';
      await api.approvePlan(incId);
      if (agentState) {
        setAgentState({ ...agentState, approval_status: 'APPROVED', execution_status: 'SIMULATED' });
      }
    } catch (err) {
      console.error('Approval failed:', err);
    }
  };

  const handleRejectPlan = async (reason: string) => {
    try {
      const incId = incident?.id || 'inc-vijayawada-01';
      await api.rejectPlan(incId, reason);
      if (agentState) {
        setAgentState({ ...agentState, approval_status: 'REJECTED' });
      }
    } catch (err) {
      console.error('Rejection failed:', err);
    }
  };

  const handleModifyPlan = async (mods: Record<string, unknown>) => {
    try {
      const incId = incident?.id || 'inc-vijayawada-01';
      await api.modifyPlan(incId, mods);
      if (agentState) {
        setAgentState({ ...agentState, approval_status: 'MODIFIED' });
      }
    } catch (err) {
      console.error('Modification failed:', err);
    }
  };

  // Analytics data
  const zoneRiskData = zones.map(z => ({
    name: z.name,
    damage: z.damageScore,
    survival: z.survivalProbability,
    population: z.population,
  }));

  const resourceData = [
    { name: 'Available', value: resources.filter(r => r.status === 'available').length, color: '#22c55e' },
    { name: 'Deployed', value: resources.filter(r => r.status === 'deployed').length, color: '#3b82f6' },
    { name: 'Maintenance', value: resources.filter(r => r.status === 'maintenance').length, color: '#ef4444' },
  ];

  const timelineStats = [
    { time: '00:00', incidents: 2, alerts: 5 },
    { time: '01:00', incidents: 3, alerts: 8 },
    { time: '02:00', incidents: 5, alerts: 12 },
    { time: '03:00', incidents: 4, alerts: 10 },
    { time: '04:00', incidents: 6, alerts: 15 },
    { time: '05:00', incidents: 8, alerts: 20 },
  ];

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <Shield className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <span className="font-bold text-foreground block leading-none text-sm">CrisisMind AI</span>
            <span className="text-[10px] text-muted-foreground font-mono">Agentic DSS</span>
          </div>
        </div>
      </div>
      
      <nav className="flex-1 p-4 space-y-2">
        <Button 
          variant={currentView === 'dashboard' ? 'default' : 'ghost'} 
          className="w-full justify-start gap-2 text-xs font-semibold"
          onClick={() => setCurrentView('dashboard')}
        >
          <LayoutDashboard className="w-4 h-4" />
          Command Center
        </Button>

        <Button 
          variant={currentView === 'agents' ? 'default' : 'ghost'} 
          className="w-full justify-start gap-2 text-xs font-semibold"
          onClick={() => setCurrentView('agents')}
        >
          <Bot className="w-4 h-4 text-purple-400" />
          Agent Operations
        </Button>

        <Button 
          variant={currentView === 'approval' ? 'default' : 'ghost'} 
          className="w-full justify-start gap-2 text-xs font-semibold"
          onClick={() => setCurrentView('approval')}
        >
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          Decision Approval
        </Button>

        <Button 
          variant={currentView === 'map' ? 'default' : 'ghost'} 
          className="w-full justify-start gap-2 text-xs font-semibold"
          onClick={() => setCurrentView('map')}
        >
          <Map className="w-4 h-4" />
          Interactive Map
        </Button>

        <Button 
          variant={currentView === 'analytics' ? 'default' : 'ghost'} 
          className="w-full justify-start gap-2 text-xs font-semibold"
          onClick={() => setCurrentView('analytics')}
        >
          <BarChart3 className="w-4 h-4" />
          Analytics
        </Button>

        <Button 
          variant={currentView === 'livefeed' ? 'default' : 'ghost'} 
          className="w-full justify-start gap-2 text-xs font-semibold"
          onClick={() => setCurrentView('livefeed')}
        >
          <Activity className="w-4 h-4" />
          Live Feed
        </Button>
      </nav>
      
      <div className="p-4 border-t border-border space-y-2">
        <Button variant="ghost" className="w-full justify-start gap-2 text-muted-foreground">
          <Settings className="w-4 h-4" />
          Settings
        </Button>
        <Button variant="ghost" className="w-full justify-start gap-2 text-muted-foreground">
          <HelpCircle className="w-4 h-4" />
          Help
        </Button>
      </div>
    </div>
  );

  // Map View Component
  const MapView = () => (
    <div className="h-full flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
          <Map className="w-5 h-5 text-primary" />
          Interactive Operations Map
        </h2>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="gap-1">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            {zones.filter(z => z.riskLevel === 'critical').length} Critical
          </Badge>
          <Badge variant="outline" className="gap-1">
            <div className="w-2 h-2 rounded-full bg-orange-500" />
            {zones.filter(z => z.riskLevel === 'high').length} High
          </Badge>
          <Badge variant="outline" className="gap-1">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            {resources.filter(r => r.status === 'available').length} Resources Available
          </Badge>
        </div>
      </div>
      
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div className="lg:col-span-3 h-[600px] bg-card rounded-lg border border-border overflow-hidden">
          <DisasterMap
            zones={zones}
            resources={resources}
            incident={incident}
            selectedZone={selectedZone}
            onZoneSelect={setSelectedZone}
          />
        </div>
        
        <div className="space-y-4">
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Zone Details
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selectedZone ? (
                (() => {
                  const zone = zones.find(z => z.id === selectedZone);
                  if (!zone) return null;
                  return (
                    <div className="space-y-3">
                      <div>
                        <p className="text-lg font-bold text-foreground">{zone.name}</p>
                        <Badge 
                          variant="outline" 
                          className={
                            zone.riskLevel === 'critical' ? 'border-red-500 text-red-500' :
                            zone.riskLevel === 'high' ? 'border-orange-500 text-orange-500' :
                            zone.riskLevel === 'medium' ? 'border-yellow-500 text-yellow-500' :
                            'border-green-500 text-green-500'
                          }
                        >
                          {zone.riskLevel.toUpperCase()}
                        </Badge>
                      </div>
                      <div className="space-y-2">
                        <div>
                          <p className="text-xs text-muted-foreground">Damage Score</p>
                          <Progress value={zone.damageScore} className="h-2 mt-1" />
                          <p className="text-sm font-medium text-foreground">{zone.damageScore}%</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Survival Probability</p>
                          <Progress value={zone.survivalProbability} className="h-2 mt-1" />
                          <p className="text-sm font-medium text-foreground">{zone.survivalProbability}%</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Population</p>
                          <p className="text-sm font-medium text-foreground">{zone.population.toLocaleString()}</p>
                        </div>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground mb-1">Assigned Resources</p>
                        <div className="flex flex-wrap gap-1">
                          {resources.filter(r => r.assignment === zone.id).map(r => (
                            <Badge key={r.id} variant="secondary" className="text-[10px]">
                              {r.type.replace('_', ' ')}
                            </Badge>
                          ))}
                          {resources.filter(r => r.assignment === zone.id).length === 0 && (
                            <span className="text-xs text-muted-foreground">None assigned</span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })()
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  Click on a zone to view details
                </p>
              )}
            </CardContent>
          </Card>
          
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button size="sm" className="w-full" disabled={!selectedZone}>
                <Satellite className="w-4 h-4 mr-2" />
                Request Satellite Imagery
              </Button>
              <Button size="sm" variant="outline" className="w-full" disabled={!selectedZone}>
                <Radio className="w-4 h-4 mr-2" />
                Deploy Drone Survey
              </Button>
              <Button size="sm" variant="outline" className="w-full" disabled={!selectedZone}>
                <AlertTriangle className="w-4 h-4 mr-2" />
                Issue Evacuation Alert
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );

  // Analytics View Component
  const AnalyticsView = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-primary" />
          Analytics & Insights
        </h2>
        <div className="flex items-center gap-2">
          <Badge variant="outline">Last Updated: Just now</Badge>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="border-border">
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Total Population at Risk</p>
            <p className="text-2xl font-bold text-foreground">
              {zones.reduce((acc, z) => acc + z.population, 0).toLocaleString()}
            </p>
            <p className="text-xs text-red-500">
              {zones.filter(z => z.riskLevel === 'critical' || z.riskLevel === 'high')
                .reduce((acc, z) => acc + z.population, 0).toLocaleString()} in danger zones
            </p>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Avg Damage Severity</p>
            <p className="text-2xl font-bold text-foreground">
              {Math.round(zones.reduce((acc, z) => acc + z.damageScore, 0) / zones.length)}%
            </p>
            <p className="text-xs text-orange-500">Critical level</p>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Resource Utilization</p>
            <p className="text-2xl font-bold text-foreground">
              {Math.round((resources.filter(r => r.status === 'deployed').length / resources.length) * 100)}%
            </p>
            <p className="text-xs text-blue-500">
              {resources.filter(r => r.status === 'deployed').length} of {resources.length} deployed
            </p>
          </CardContent>
        </Card>
        <Card className="border-border">
          <CardContent className="p-4">
            <p className="text-xs text-muted-foreground">Response Time</p>
            <p className="text-2xl font-bold text-foreground">12m</p>
            <p className="text-xs text-green-500">Within target</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Zone Risk Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={zoneRiskData}>
                  <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-45} textAnchor="end" height={60} />
                  <YAxis />
                  <Tooltip 
                    contentStyle={{ background: '#1f2937', border: 'none', borderRadius: '4px' }}
                  />
                  <Bar dataKey="damage" fill="#ef4444" name="Damage %" />
                  <Bar dataKey="survival" fill="#22c55e" name="Survival %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Resource Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={resourceData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {resourceData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ background: '#1f2937', border: 'none', borderRadius: '4px' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex justify-center gap-4 mt-2">
              {resourceData.map(item => (
                <div key={item.name} className="flex items-center gap-1">
                  <div className="w-3 h-3 rounded-full" style={{ background: item.color }} />
                  <span className="text-xs text-muted-foreground">{item.name} ({item.value})</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Incident Timeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={timelineStats}>
                  <XAxis dataKey="time" tick={{ fontSize: 10 }} />
                  <YAxis />
                  <Tooltip 
                    contentStyle={{ background: '#1f2937', border: 'none', borderRadius: '4px' }}
                  />
                  <Line type="monotone" dataKey="incidents" stroke="#ef4444" name="Incidents" strokeWidth={2} />
                  <Line type="monotone" dataKey="alerts" stroke="#f97316" name="Alerts" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-muted-foreground">
              AI Model Performance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {[
              { name: 'Damage Detection (YOLOv8)', accuracy: 94, latency: '45ms' },
              { name: 'Building Collapse (ResNet50)', accuracy: 91, latency: '32ms' },
              { name: 'Sentiment Analysis (BERT)', accuracy: 89, latency: '28ms' },
              { name: 'Risk Forecasting (LSTM)', accuracy: 87, latency: '18ms' },
            ].map(model => (
              <div key={model.name} className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-foreground">{model.name}</span>
                  <span className="text-xs text-muted-foreground">{model.latency}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Progress value={model.accuracy} className="h-2 flex-1" />
                  <span className="text-xs font-medium text-foreground w-10">{model.accuracy}%</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );

  // Live Feed View Component
  const LiveFeedView = () => (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
          <Activity className="w-5 h-5 text-primary" />
          Live Operations Feed
        </h2>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-sm text-muted-foreground">Live</span>
          </div>
          <Button size="sm" variant={isSimulating ? 'default' : 'outline'} onClick={toggleSimulation}>
            {isSimulating ? 'Stop Simulation' : 'Start Simulation'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Live Sensor Data */}
        <div className="space-y-4">
          <SensorDataPanel sensors={sensorData} />
          
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Data Streams
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {[
                { name: 'Satellite Feed', status: 'connected', rate: '2.4 MB/s' },
                { name: 'Drone Stream 1', status: 'connected', rate: '1.8 MB/s' },
                { name: 'IoT Sensors', status: 'connected', rate: '156 KB/s' },
                { name: 'Social Media API', status: 'connected', rate: '45 KB/s' },
              ].map(stream => (
                <div key={stream.name} className="flex items-center justify-between p-2 bg-muted rounded-lg">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-sm text-foreground">{stream.name}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">{stream.rate}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Live Timeline */}
        <div>
          <EmergencyTimeline events={timelineEvents} />
        </div>

        {/* Social Media & Alerts */}
        <div className="space-y-4">
          <SocialMediaPanel reports={socialReports} />
          
          <Card className="border-border">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Radio className="w-4 h-4" />
                Emergency Calls
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {[
                    { id: 'CALL-2847', type: 'Medical Emergency', location: 'Downtown District', time: '2m ago', priority: 'high' },
                    { id: 'CALL-2846', type: 'Trapped Persons', location: 'Industrial Area', time: '5m ago', priority: 'critical' },
                    { id: 'CALL-2845', type: 'Fire Report', location: 'Residential North', time: '8m ago', priority: 'high' },
                    { id: 'CALL-2844', type: 'Injury Report', location: 'Safe Zone East', time: '12m ago', priority: 'medium' },
                    { id: 'CALL-2843', type: 'Structural Damage', location: 'Downtown District', time: '15m ago', priority: 'high' },
                  ].map(call => (
                    <div key={call.id} className="p-2 bg-muted rounded-lg">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-mono text-muted-foreground">{call.id}</span>
                        <Badge 
                          variant="outline" 
                          className={
                            call.priority === 'critical' ? 'border-red-500 text-red-500 text-[10px]' :
                            call.priority === 'high' ? 'border-orange-500 text-orange-500 text-[10px]' :
                            'border-yellow-500 text-yellow-500 text-[10px]'
                          }
                        >
                          {call.priority}
                        </Badge>
                      </div>
                      <p className="text-sm text-foreground">{call.type}</p>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-xs text-muted-foreground">{call.location}</span>
                        <span className="text-xs text-muted-foreground">{call.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );

  // Dashboard View (Original)
  const DashboardView = () => (
    <Tabs defaultValue="overview" className="space-y-4">
      <TabsList className="bg-card border border-border">
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="analysis">Damage Analysis</TabsTrigger>
        <TabsTrigger value="intelligence">Intelligence</TabsTrigger>
      </TabsList>

      {/* Overview Tab */}
      <TabsContent value="overview" className="space-y-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Map - Takes 2 columns */}
          <div className="lg:col-span-2 space-y-4">
            <div className="h-[500px] bg-card rounded-lg border border-border overflow-hidden">
              <DisasterMap
                zones={zones}
                resources={resources}
                incident={incident}
                selectedZone={selectedZone}
                onZoneSelect={setSelectedZone}
              />
            </div>
            
            {/* Emergency Timeline */}
            <EmergencyTimeline events={timelineEvents} />
          </div>

          {/* Side Panel */}
          <div className="space-y-4">
            <RiskAssessmentPanel 
              zones={zones} 
              selectedZone={selectedZone}
            />
            <RecommendationsPanel
              recommendations={recommendations}
              onExecute={executeRecommendation}
              onDismiss={dismissRecommendation}
            />
          </div>
        </div>
      </TabsContent>

      {/* Damage Analysis Tab */}
      <TabsContent value="analysis" className="space-y-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <DamageDetectionPanel
            detections={detections}
            currentDetection={currentDetection}
            isAnalyzing={isAnalyzing}
            onUpload={uploadAndAnalyze}
            onSelect={selectDetection}
            onClear={clearDetections}
          />
          
          {/* Analysis Stats */}
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-card p-4 rounded-lg border border-border">
                <p className="text-sm text-muted-foreground">Images Analyzed</p>
                <p className="text-2xl font-bold text-foreground">{detections.length}</p>
              </div>
              <div className="bg-card p-4 rounded-lg border border-border">
                <p className="text-sm text-muted-foreground">Avg Damage Score</p>
                <p className="text-2xl font-bold text-foreground">
                  {detections.length > 0 
                    ? Math.round(detections.reduce((a, d) => a + d.damageScore, 0) / detections.length)
                    : 0}%
                </p>
              </div>
            </div>
            
            {/* AI Model Status */}
            <div className="bg-card p-4 rounded-lg border border-border">
              <h4 className="text-sm font-medium text-foreground mb-3">AI Models Status</h4>
              <div className="space-y-2">
                {[
                  { name: 'YOLOv8 Damage Detection', status: 'Active', confidence: '94%' },
                  { name: 'ResNet50 Collapse Classifier', status: 'Active', confidence: '91%' },
                  { name: 'U-Net Segmentation', status: 'Active', confidence: '89%' },
                ].map(model => (
                  <div key={model.name} className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">{model.name}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-green-500 text-xs">{model.status}</span>
                      <span className="text-xs text-muted-foreground">{model.confidence}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </TabsContent>

      {/* Intelligence Tab */}
      <TabsContent value="intelligence" className="space-y-4">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SensorDataPanel sensors={sensorData} />
          <SocialMediaPanel reports={socialReports} />
        </div>
        
        {/* Data Sources Status */}
        <div className="bg-card p-4 rounded-lg border border-border">
          <h4 className="text-sm font-medium text-foreground mb-3">Data Sources</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { name: 'Satellite Imagery', status: 'Connected', latency: '2.3s' },
              { name: 'IoT Sensors', status: 'Connected', latency: '0.8s' },
              { name: 'Social Media APIs', status: 'Connected', latency: '1.2s' },
              { name: 'Emergency Calls', status: 'Connected', latency: '0.5s' },
            ].map(source => (
              <div key={source.name} className="p-3 bg-muted rounded-lg">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-sm font-medium text-foreground">{source.name}</span>
                </div>
                <p className="text-xs text-muted-foreground">{source.status}</p>
                <p className="text-xs text-muted-foreground">Latency: {source.latency}</p>
              </div>
            ))}
          </div>
        </div>
      </TabsContent>
    </Tabs>
  );

  return (
    <div className="min-h-screen bg-background flex">
      {/* Desktop Sidebar */}
      <aside className={`hidden lg:block border-r border-border bg-card transition-all duration-300 ${
        sidebarOpen ? 'w-64' : 'w-0 overflow-hidden'
      }`}>
        <SidebarContent />
      </aside>

      {/* Mobile Sidebar */}
      <Sheet>
        <SheetTrigger asChild className="lg:hidden">
          <Button variant="ghost" size="icon" className="absolute top-4 left-4 z-50">
            <Menu className="w-5 h-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0">
          <SidebarContent />
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <Header 
          incident={incident}
          isSimulating={isSimulating}
          onToggleSimulation={toggleSimulation}
        />

        {/* Resource Status Bar */}
        <ResourceStatusBar resources={resources} />

        {/* Content Area */}
        <div className="flex-1 p-4 overflow-auto">
          {currentView === 'dashboard' && <DashboardView />}
          {currentView === 'agents' && (
            <AgentOperationsPanel 
              agentState={agentState} 
              isRunning={isAgentRunning} 
              onRunWorkflow={handleRunAgentWorkflow} 
            />
          )}
          {currentView === 'approval' && (
            <DecisionApprovalCenter 
              agentState={agentState} 
              onApprove={handleApprovePlan} 
              onReject={handleRejectPlan} 
              onModify={handleModifyPlan} 
            />
          )}
          {currentView === 'map' && <MapView />}
          {currentView === 'analytics' && <AnalyticsView />}
          {currentView === 'livefeed' && <LiveFeedView />}
        </div>
      </main>

      {/* Sidebar Toggle (Desktop) */}
      <Button
        variant="ghost"
        size="icon"
        className="hidden lg:flex fixed bottom-4 left-4 z-50"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </Button>
    </div>
  );
}

export default App;
