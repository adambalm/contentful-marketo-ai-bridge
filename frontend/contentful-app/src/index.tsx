import { GlobalStyles } from '@contentful/f36-components';
import { SDKProvider } from '@contentful/react-apps-toolkit';

import { createRoot } from 'react-dom/client';
import App from './App';
import LocalhostWarning from './components/LocalhostWarning';
import DevDebug from './DevDebug';

const container = document.getElementById('root')!;
const root = createRoot(container);

if (process.env.NODE_ENV === 'development' && window.self === window.top) {
  // In dev outside Contentful, render the debug page instead of the warning
  root.render(<DevDebug />);
} else {
  root.render(
    <SDKProvider>
      <GlobalStyles />
      <App />
    </SDKProvider>
  );
}
