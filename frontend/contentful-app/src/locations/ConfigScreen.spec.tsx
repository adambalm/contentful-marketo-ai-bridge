import ConfigScreen from './ConfigScreen';
import { render } from '@testing-library/react';
import { mockCma, mockSdk } from '../../test/mocks';
import { vi } from 'vitest';

vi.mock('@contentful/react-apps-toolkit', () => ({
  useSDK: () => mockSdk,
  useCMA: () => mockCma,
}));

describe('Config Screen component', () => {
  it('renders configuration heading and label', () => {
    const { getByText } = render(<ConfigScreen />);

    expect(
      getByText('AI Content Activation Engine - Configuration')
    ).toBeInTheDocument();

    expect(getByText('Backend API URL')).toBeInTheDocument();
  });
});
