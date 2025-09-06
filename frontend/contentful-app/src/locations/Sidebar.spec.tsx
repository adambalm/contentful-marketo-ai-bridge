import Sidebar from './Sidebar';
import { render } from '@testing-library/react';
import { mockCma, mockSdk } from '../../test/mocks';
import { vi } from 'vitest';

vi.mock('@contentful/react-apps-toolkit', () => ({
  useSDK: () => mockSdk,
  useCMA: () => mockCma,
}));

describe('Sidebar component', () => {
  it('renders activation UI elements', () => {
    const { getByText } = render(<Sidebar />);

    // Subheading/title
    expect(getByText('AI Content Activation Engine')).toBeInTheDocument();

    // Primary action button
    expect(getByText('Activate in Marketo')).toBeInTheDocument();
  });
});
