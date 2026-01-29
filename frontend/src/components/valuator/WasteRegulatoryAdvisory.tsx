import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Button } from '@/components/ui/button';
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  FileText,
  ExternalLink,
  Shield,
  Package,
  Building2,
  Globe,
} from 'lucide-react';
import {
  RouteAdvisory,
  RegulatoryRequirementsResponse,
  PermitItem,
} from '@/types/battery';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface WasteRegulatoryAdvisoryProps {
  routeAdvisory?: RouteAdvisory;
  regulatoryRequirements?: RegulatoryRequirementsResponse;
  loading?: boolean;
}

export const WasteRegulatoryAdvisory = ({
  routeAdvisory,
  regulatoryRequirements,
  loading = false,
}: WasteRegulatoryAdvisoryProps) => {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    route: true,
    origin: false,
    destination: false,
    basel: false,
    permits: false,
    packaging: false,
    documentation: false,
  });

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  if (loading) {
    return (
      <Card className="bg-card rounded-xl border-border card-shadow">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-foreground uppercase tracking-wider">
            <Shield className="h-4 w-4 text-primary" />
            Regulatory Advisory
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Loading regulatory information...</p>
        </CardContent>
      </Card>
    );
  }

  if (!routeAdvisory) {
    return null;
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'allowed':
        return 'bg-profit/20 text-profit border-profit/30';
      case 'restricted':
        return 'bg-warning/20 text-warning-foreground border-warning/30';
      case 'blocked':
        return 'bg-destructive/20 text-destructive border-destructive/30';
      default:
        return 'bg-muted text-muted-foreground border-border';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'allowed':
        return <CheckCircle2 className="h-5 w-5 text-profit" />;
      case 'restricted':
        return <AlertTriangle className="h-5 w-5 text-warning" />;
      case 'blocked':
        return <AlertCircle className="h-5 w-5 text-destructive" />;
      default:
        return <AlertCircle className="h-5 w-5 text-muted-foreground" />;
    }
  };

  return (
    <Card className="bg-card rounded-xl border-border card-shadow">
      <CardHeader className="pb-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-foreground uppercase tracking-wider">
          <Shield className="h-4 w-4 text-primary" />
          Waste Battery Regulatory Advisory
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Route Status */}
        <Collapsible
          open={expandedSections.route}
          onOpenChange={() => toggleSection('route')}
        >
          <div className="space-y-3">
            <CollapsibleTrigger asChild>
              <Button variant="ghost" className="w-full justify-between p-3 h-auto">
                <div className="flex items-center gap-2">
                  {getStatusIcon(routeAdvisory.status)}
                  <span className="font-semibold">Route Status</span>
                </div>
                {expandedSections.route ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>
            </CollapsibleTrigger>

            <CollapsibleContent className="space-y-3">
              <Badge
                variant="outline"
                className={`${getStatusColor(routeAdvisory.status)} text-sm px-3 py-1`}
              >
                {routeAdvisory.status.toUpperCase()}
              </Badge>

              {routeAdvisory.processing_time && (
                <p className="text-sm text-muted-foreground">
                  <strong>Processing Time:</strong> {routeAdvisory.processing_time}
                </p>
              )}

              {routeAdvisory.requirements.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">Required:</p>
                  <ul className="space-y-1">
                    {routeAdvisory.requirements.map((req, idx) => (
                      <li key={idx} className="text-sm flex items-start gap-2">
                        <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                        <span>{req}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {routeAdvisory.warnings.length > 0 && (
                <Alert variant="destructive" className="mt-3">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle>Warnings</AlertTitle>
                  <AlertDescription>
                    <ul className="space-y-1 mt-2">
                      {routeAdvisory.warnings.map((warning, idx) => (
                        <li key={idx} className="text-sm">
                          {warning}
                        </li>
                      ))}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}
            </CollapsibleContent>
          </div>
        </Collapsible>

        {regulatoryRequirements && (
          <>
            {/* Origin Regulations */}
            <Collapsible
              open={expandedSections.origin}
              onOpenChange={() => toggleSection('origin')}
            >
              <div className="border-t pt-4">
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" className="w-full justify-between p-3 h-auto">
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4" />
                      <span className="font-medium">
                        Origin: {regulatoryRequirements.regulations.origin.country}
                      </span>
                    </div>
                    {expandedSections.origin ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </CollapsibleTrigger>

                <CollapsibleContent className="space-y-3 px-3">
                  <div className="text-sm space-y-2">
                    {regulatoryRequirements.regulations.origin.framework && (
                      <p>
                        <strong>Framework:</strong>{' '}
                        {regulatoryRequirements.regulations.origin.framework}
                      </p>
                    )}
                    {regulatoryRequirements.regulations.origin.authority && (
                      <p>
                        <strong>Authority:</strong>{' '}
                        {regulatoryRequirements.regulations.origin.authority}
                      </p>
                    )}
                    {regulatoryRequirements.regulations.origin.links &&
                      Object.entries(regulatoryRequirements.regulations.origin.links).map(
                        ([key, url]) => (
                          <a
                            key={key}
                            href={url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-primary hover:underline"
                          >
                            <ExternalLink className="h-3 w-3" />
                            {key.replace(/_/g, ' ')}
                          </a>
                        )
                      )}
                  </div>
                </CollapsibleContent>
              </div>
            </Collapsible>

            {/* Destination Regulations */}
            <Collapsible
              open={expandedSections.destination}
              onOpenChange={() => toggleSection('destination')}
            >
              <div className="border-t pt-4">
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" className="w-full justify-between p-3 h-auto">
                    <div className="flex items-center gap-2">
                      <Globe className="h-4 w-4" />
                      <span className="font-medium">
                        Destination: {regulatoryRequirements.regulations.destination.country}
                      </span>
                    </div>
                    {expandedSections.destination ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </CollapsibleTrigger>

                <CollapsibleContent className="space-y-3 px-3">
                  <div className="text-sm space-y-2">
                    {regulatoryRequirements.regulations.destination.framework && (
                      <p>
                        <strong>Framework:</strong>{' '}
                        {regulatoryRequirements.regulations.destination.framework}
                      </p>
                    )}
                    {regulatoryRequirements.regulations.destination.authority && (
                      <p>
                        <strong>Authority:</strong>{' '}
                        {regulatoryRequirements.regulations.destination.authority}
                      </p>
                    )}
                  </div>
                </CollapsibleContent>
              </div>
            </Collapsible>

            {/* Basel Convention Requirements */}
            {regulatoryRequirements.checklist.basel_convention.length > 0 && (
              <Collapsible
                open={expandedSections.basel}
                onOpenChange={() => toggleSection('basel')}
              >
                <div className="border-t pt-4">
                  <CollapsibleTrigger asChild>
                    <Button variant="ghost" className="w-full justify-between p-3 h-auto">
                      <div className="flex items-center gap-2">
                        <Shield className="h-4 w-4" />
                        <span className="font-medium">Basel Convention</span>
                      </div>
                      {expandedSections.basel ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </Button>
                  </CollapsibleTrigger>

                  <CollapsibleContent className="space-y-2 px-3">
                    {regulatoryRequirements.checklist.basel_convention.map((item, idx) => (
                      <div key={idx} className="p-3 bg-primary/10 border border-primary/20 rounded-lg text-sm">
                        <p className="font-medium">{item.name}</p>
                        <p className="text-muted-foreground text-xs mt-1">{item.description}</p>
                        {item.applies_to && (
                          <p className="text-xs text-primary mt-1">
                            Applies to: {item.applies_to}
                          </p>
                        )}
                      </div>
                    ))}
                  </CollapsibleContent>
                </div>
              </Collapsible>
            )}

            {/* Permits Checklist */}
            {regulatoryRequirements.checklist.export_permits.length > 0 && (
              <Collapsible
                open={expandedSections.permits}
                onOpenChange={() => toggleSection('permits')}
              >
                <div className="border-t pt-4">
                  <CollapsibleTrigger asChild>
                    <Button variant="ghost" className="w-full justify-between p-3 h-auto">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        <span className="font-medium">Required Permits</span>
                        <Badge variant="secondary">
                          {regulatoryRequirements.checklist.export_permits.length}
                        </Badge>
                      </div>
                      {expandedSections.permits ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </Button>
                  </CollapsibleTrigger>

                  <CollapsibleContent className="space-y-2 px-3">
                    {regulatoryRequirements.checklist.export_permits.map((permit, idx) => (
                      <div key={idx} className="p-3 border rounded-lg space-y-1">
                        <div className="flex items-start justify-between">
                          <p className="font-medium text-sm">{permit.name}</p>
                          {permit.required === true && (
                            <Badge variant="destructive" className="text-xs">
                              Required
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          <Building2 className="h-3 w-3 inline mr-1" />
                          {permit.agency}
                        </p>
                        {permit.processing_time && (
                          <p className="text-xs text-muted-foreground">
                            Processing: {permit.processing_time}
                          </p>
                        )}
                        {permit.url && (
                          <a
                            href={permit.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-primary hover:underline flex items-center gap-1"
                          >
                            <ExternalLink className="h-3 w-3" />
                            Apply online
                          </a>
                        )}
                      </div>
                    ))}
                  </CollapsibleContent>
                </div>
              </Collapsible>
            )}

            {/* Packaging Requirements */}
            <Collapsible
              open={expandedSections.packaging}
              onOpenChange={() => toggleSection('packaging')}
            >
              <div className="border-t pt-4">
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" className="w-full justify-between p-3 h-auto">
                    <div className="flex items-center gap-2">
                      <Package className="h-4 w-4" />
                      <span className="font-medium">Packaging & Transport</span>
                    </div>
                    {expandedSections.packaging ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </CollapsibleTrigger>

                <CollapsibleContent className="space-y-3 px-3">
                  {regulatoryRequirements.checklist.packaging.un_classification && (
                    <div className="p-3 bg-warning/10 border border-warning/30 rounded-lg text-sm">
                      <p className="font-medium">UN Classification</p>
                      <p className="text-xs mt-1">
                        {regulatoryRequirements.checklist.packaging.un_classification.un_number} -{' '}
                        {regulatoryRequirements.checklist.packaging.un_classification.class}
                      </p>
                    </div>
                  )}

                  {regulatoryRequirements.checklist.packaging.requirements && (
                    <div className="space-y-1">
                      <p className="text-sm font-medium">Requirements:</p>
                      <ul className="space-y-1">
                        {regulatoryRequirements.checklist.packaging.requirements.map(
                          (req, idx) => (
                            <li key={idx} className="text-xs flex items-start gap-2">
                              <CheckCircle2 className="h-3 w-3 text-profit mt-0.5 flex-shrink-0" />
                              <span>{req}</span>
                            </li>
                          )
                        )}
                      </ul>
                    </div>
                  )}
                </CollapsibleContent>
              </div>
            </Collapsible>

            {/* Documentation Checklist */}
            {regulatoryRequirements.checklist.documentation.length > 0 && (
              <Collapsible
                open={expandedSections.documentation}
                onOpenChange={() => toggleSection('documentation')}
              >
                <div className="border-t pt-4">
                  <CollapsibleTrigger asChild>
                    <Button variant="ghost" className="w-full justify-between p-3 h-auto">
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4" />
                        <span className="font-medium">Required Documentation</span>
                        <Badge variant="secondary">
                          {regulatoryRequirements.checklist.documentation.length}
                        </Badge>
                      </div>
                      {expandedSections.documentation ? (
                        <ChevronUp className="h-4 w-4" />
                      ) : (
                        <ChevronDown className="h-4 w-4" />
                      )}
                    </Button>
                  </CollapsibleTrigger>

                  <CollapsibleContent className="space-y-2 px-3">
                    <div className="grid gap-2">
                      {regulatoryRequirements.checklist.documentation.map((doc, idx) => (
                        <div key={idx} className="flex items-start gap-2 p-2 bg-muted rounded">
                          <CheckCircle2 className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium">{doc.name}</p>
                            <p className="text-xs text-muted-foreground">{doc.description}</p>
                          </div>
                          {doc.required === true && (
                            <Badge variant="outline" className="text-xs">
                              Required
                            </Badge>
                          )}
                        </div>
                      ))}
                    </div>
                  </CollapsibleContent>
                </div>
              </Collapsible>
            )}
          </>
        )}

        {/* General Advisory */}
        <Alert className="mt-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="text-xs">
            This advisory is for informational purposes. Always consult with legal counsel and
            regulatory authorities before shipping hazardous waste materials internationally.
            Regulations change frequently and vary by jurisdiction.
          </AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );
};
