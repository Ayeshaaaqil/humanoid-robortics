import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/chat',
    component: ComponentCreator('/chat', '4b9'),
    exact: true
  },
  {
    path: '/chatbot',
    component: ComponentCreator('/chatbot', '522'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', 'efa'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '8fd'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', '0db'),
            routes: [
              {
                path: '/docs/chapter-1-introduction-to-physical-ai',
                component: ComponentCreator('/docs/chapter-1-introduction-to-physical-ai', '2d1'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/chapter-2-basics-of-humanoid-robotics',
                component: ComponentCreator('/docs/chapter-2-basics-of-humanoid-robotics', '375'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/chapter-3-ros-2-fundamentals',
                component: ComponentCreator('/docs/chapter-3-ros-2-fundamentals', '0cb'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/chapter-4-digital-twin-simulation',
                component: ComponentCreator('/docs/chapter-4-digital-twin-simulation', '07a'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/chapter-5-vision-language-action-systems',
                component: ComponentCreator('/docs/chapter-5-vision-language-action-systems', '9f2'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/chapter-6-capstone-ai-robot-pipeline',
                component: ComponentCreator('/docs/chapter-6-capstone-ai-robot-pipeline', 'd57'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '853'),
                exact: true
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
