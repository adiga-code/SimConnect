# OnlineSim - SMS Verification Service

## Overview

OnlineSim is a Telegram Web App for purchasing temporary phone numbers for SMS verification. The application provides users with virtual phone numbers from various countries to receive SMS codes for service registrations like Telegram, WhatsApp, and Discord. Built as a modern full-stack web application with a React frontend and Express backend, it's designed to integrate seamlessly with Telegram's ecosystem while providing a native mobile-first experience.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
The client is built using **React 18** with **TypeScript** in a single-page application (SPA) architecture. The UI framework leverages **shadcn/ui** components built on top of **Radix UI** primitives for accessibility and **Tailwind CSS** for styling. The application uses **Wouter** for lightweight client-side routing and **TanStack Query** for efficient server state management and caching.

The component structure follows a modular approach with reusable UI components, feature-specific components, and page-level components. The app implements a mobile-first design with bottom navigation and tab-based content organization, optimized for Telegram's Web App environment.

### Backend Architecture
The server is an **Express.js** application written in **TypeScript** using ES modules. It follows a RESTful API design pattern with modular route organization. The application implements an in-memory storage layer with a well-defined interface that can be easily swapped for database implementations.

The server includes middleware for request logging, error handling, and development-specific features. In development mode, it integrates with **Vite** for hot module replacement and serves the React application.

### Data Storage Solutions
Currently implements an **in-memory storage** system with mock data for development and testing. The storage interface (`IStorage`) is designed for easy migration to persistent databases. **Drizzle ORM** is configured for PostgreSQL with schemas defined for countries, services, orders, messages, and users, indicating the planned production database structure.

The database schema supports the core business logic with proper relationships between entities and includes features like order expiration tracking and message history.

### Authentication and Authorization
The application integrates with **Telegram's Web App API** for user authentication and identification. User sessions are managed through Telegram's secure authentication flow, eliminating the need for traditional username/password authentication. The system identifies users by their Telegram ID and maintains user balance and order history.

### External Dependencies
- **Neon Database** (@neondatabase/serverless) - Configured as the serverless PostgreSQL provider
- **Telegram Web App API** - For user authentication, haptic feedback, and platform integration
- **Drizzle ORM** - Type-safe database ORM with PostgreSQL dialect
- **shadcn/ui + Radix UI** - Comprehensive component library for accessible UI components
- **TanStack Query** - Server state management and caching
- **Tailwind CSS** - Utility-first CSS framework with custom theming
- **Zod** - Runtime type validation and schema definition

The application is structured to support both development and production environments with appropriate tooling for each. The monorepo structure with shared schemas ensures type safety across the full stack while maintaining clear separation of concerns between client and server code.