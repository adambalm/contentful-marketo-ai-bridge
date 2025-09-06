import { useMemo, lazy, Suspense } from 'react';
import { locations } from '@contentful/app-sdk';
const ConfigScreen = lazy(() => import('./locations/ConfigScreen'));
const Field = lazy(() => import('./locations/Field'));
const EntryEditor = lazy(() => import('./locations/EntryEditor'));
const Dialog = lazy(() => import('./locations/Dialog'));
const Sidebar = lazy(() => import('./locations/Sidebar'));
const Page = lazy(() => import('./locations/Page'));
const Home = lazy(() => import('./locations/Home'));
import { useSDK } from '@contentful/react-apps-toolkit';
import DevDebug from './DevDebug';

const ComponentLocationSettings = {
  [locations.LOCATION_APP_CONFIG]: ConfigScreen,
  [locations.LOCATION_ENTRY_FIELD]: Field,
  [locations.LOCATION_ENTRY_EDITOR]: EntryEditor,
  [locations.LOCATION_DIALOG]: Dialog,
  [locations.LOCATION_ENTRY_SIDEBAR]: Sidebar,
  [locations.LOCATION_PAGE]: Page,
  [locations.LOCATION_HOME]: Home,
};

const App = () => {
  const sdk = useSDK();

  const Component = useMemo(() => {
    for (const [location, component] of Object.entries(ComponentLocationSettings)) {
      if (sdk.location.is(location)) {
        return component;
      }
    }
  }, [sdk.location]);

  if (Component) {
    return (
      <Suspense fallback={null}>
        <Component />
      </Suspense>
    );
  }
  // When not running inside Contentful, show dev-only debug view
  return <DevDebug />;
};

export default App;
