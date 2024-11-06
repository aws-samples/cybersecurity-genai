import { FunctionComponent } from 'react';
import { SideNavigation } from '@cloudscape-design/components';
import { ThemeMode } from '../../types';
import { useLocation } from 'react-router-dom';

interface NavigationProps {
  onThemeToggle: () => void;
  currentTheme: ThemeMode;
}

const Navigation: FunctionComponent<NavigationProps> = ({ onThemeToggle, currentTheme }) => {
  const location = useLocation();

  const navItems = [
    {
      type: "section" as const,
      text: "Menu",
      items: [
        { 
          type: "link" as const, 
          text: "Chat", 
          href: "/chat",
          active: location.pathname === '/chat'
        },
        { 
          type: "link" as const, 
          text: "About", 
          href: "/about",
          active: location.pathname === '/about'
        }
      ]
    }
  ];

  return (
    <SideNavigation
      items={navItems}
      header={{
        href: "/chat",
        text: "Navigation"
      }}
      activeHref={location.pathname}
    />
  );
};

export default Navigation;
