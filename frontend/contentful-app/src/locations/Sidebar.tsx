import { useState } from 'react';
import {
  Paragraph,
  Button,
  Stack,
  Note,
  Spinner,
  Card,
  Badge,
  Subheading,
  Text,
  Flex
} from '@contentful/f36-components';
import { SidebarAppSDK } from '@contentful/app-sdk';
import { useSDK } from '@contentful/react-apps-toolkit';

interface ActivationResult {
  activation_id: string;
  entry_id: string;
  status: 'success' | 'error';
  processing_time: number;
  enrichment_data?: {
    seo_score?: number;
    suggested_meta_description?: string;
    keywords?: string[];
  };
  errors?: string[];
  timestamp: string;
}

const Sidebar = () => {
  const sdk = useSDK<SidebarAppSDK>();
  const [isActivating, setIsActivating] = useState(false);
  const [lastResult, setLastResult] = useState<ActivationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Get the backend URL from app parameters (configured during app installation)
  const backendUrl = sdk.parameters.installation?.backendUrl || 'http://localhost:8000';

  const handleActivate = async () => {
    setIsActivating(true);
    setError(null);

    try {
      const entryId = sdk.entry.getSys().id;
      
      const response = await fetch(`${backendUrl}/activate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          entry_id: entryId,
          marketo_list_id: 'ML_DEMO_001', // Default list for MVP
          enrichment_enabled: true
        }),
      });

      const result: ActivationResult = await response.json();
      
      if (!response.ok) {
        throw new Error(result.errors?.join(', ') || 'Activation failed');
      }

      setLastResult(result);
      
      // Show success notification
      sdk.notifier.success('Content successfully activated in Marketo!');

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      sdk.notifier.error(`Activation failed: ${errorMessage}`);
    } finally {
      setIsActivating(false);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Stack spacing="spacingM">
      <Subheading>AI Content Activation Engine</Subheading>
      <Paragraph>
        Enrich and activate this content in Marketo with AI-powered metadata generation.
      </Paragraph>

      {/* Activation Button */}
      <Button
        variant="primary"
        size="medium"
        onClick={handleActivate}
        isDisabled={isActivating}
        isLoading={isActivating}
      >
        {isActivating ? 'Activating...' : 'Activate in Marketo'}
      </Button>

      {/* Loading State */}
      {isActivating && (
        <Card>
          <Flex alignItems="center" gap="spacingS">
            <Spinner />
            <Text>Processing activation with AI enrichment...</Text>
          </Flex>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Note variant="negative" title="Activation Failed">
          {error}
        </Note>
      )}

      {/* Success Result Display */}
      {lastResult && !error && (
        <Card>
          <Stack spacing="spacingS">
            <Flex alignItems="center" gap="spacingS">
              <Subheading>Last Activation</Subheading>
              <Badge
                variant={lastResult.status === 'success' ? 'positive' : 'negative'}
              >
                {lastResult.status}
              </Badge>
            </Flex>
            
            <Text fontSize="fontSizeS" fontColor="gray600">
              {formatTimestamp(lastResult.timestamp)} • 
              Processed in {lastResult.processing_time.toFixed(2)}s
            </Text>

            {/* AI Enrichment Results */}
            {lastResult.enrichment_data && (
              <Stack spacing="spacingXs">
                <Text fontWeight="fontWeightMedium">AI Enrichment Results:</Text>
                
                {lastResult.enrichment_data.seo_score && (
                  <Text fontSize="fontSizeS">
                    SEO Score: {lastResult.enrichment_data.seo_score}/100
                  </Text>
                )}
                
                {lastResult.enrichment_data.suggested_meta_description && (
                  <Text fontSize="fontSizeS">
                    Meta Description: "{lastResult.enrichment_data.suggested_meta_description}"
                  </Text>
                )}
                
                {lastResult.enrichment_data.keywords && (
                  <Text fontSize="fontSizeS">
                    Keywords: {lastResult.enrichment_data.keywords.join(', ')}
                  </Text>
                )}
              </Stack>
            )}

            <Text fontSize="fontSizeS" fontColor="gray600">
              Activation ID: {lastResult.activation_id}
            </Text>
          </Stack>
        </Card>
      )}

      {/* Instructions */}
      <Note variant="primary" title="How it works">
        This tool validates your content, enriches it with AI-generated metadata, 
        and adds it to your Marketo campaign list. All actions are logged for audit purposes.
      </Note>
    </Stack>
  );
};

export default Sidebar;