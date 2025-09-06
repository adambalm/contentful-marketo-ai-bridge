import { useCallback, useState, useEffect } from 'react';
import { ConfigAppSDK } from '@contentful/app-sdk';
import { 
  Heading, 
  Form, 
  Paragraph, 
  Flex,
  TextInput,
  FormControl,
  Note
} from '@contentful/f36-components';
import { css } from 'emotion';
import { useSDK } from '@contentful/react-apps-toolkit';

export interface AppInstallationParameters {
  backendUrl?: string;
}

const ConfigScreen = () => {
  const [parameters, setParameters] = useState<AppInstallationParameters>({
    backendUrl: 'http://localhost:8000'
  });
  const sdk = useSDK<ConfigAppSDK>();

  const onConfigure = useCallback(async () => {
    // Get current the state of EditorInterface and other entities
    const currentState = await sdk.app.getCurrentState();

    return {
      // Parameters to be persisted as the app configuration
      parameters,
    };
  }, [parameters, sdk]);

  useEffect(() => {
    sdk.app.onConfigure(() => onConfigure());
  }, [sdk, onConfigure]);

  useEffect(() => {
    (async () => {
      // Get current parameters of the app
      const currentParameters: AppInstallationParameters | null = await sdk.app.getParameters();

      if (currentParameters) {
        setParameters(currentParameters);
      }

      // Set app as ready
      sdk.app.setReady();
    })();
  }, [sdk]);

  return (
    <Flex flexDirection="column" className={css({ margin: '80px', maxWidth: '800px' })}>
      <Form>
        <Heading>AI Content Activation Engine - Configuration</Heading>
        <Paragraph>
          Configure your AI Content Activation Engine to connect with your FastAPI backend.
        </Paragraph>

        <FormControl>
          <FormControl.Label>Backend API URL</FormControl.Label>
          <TextInput
            value={parameters.backendUrl || ''}
            onChange={(e) => setParameters({ ...parameters, backendUrl: e.target.value })}
            placeholder="https://your-backend-api.render.com"
          />
          <FormControl.HelpText>
            URL of your FastAPI backend that handles content activation
          </FormControl.HelpText>
        </FormControl>

        <Note variant="primary" title="Setup Instructions">
          <Paragraph>
            1. Deploy your FastAPI backend (e.g., to Render, Heroku, or similar)
          </Paragraph>
          <Paragraph>
            2. Enter the backend URL above (e.g., https://your-app.render.com)
          </Paragraph>
          <Paragraph>
            3. This app will appear in the sidebar of content entries
          </Paragraph>
          <Paragraph>
            4. Click "Activate in Marketo" to process content with AI enrichment
          </Paragraph>
        </Note>
      </Form>
    </Flex>
  );
};

export default ConfigScreen;
