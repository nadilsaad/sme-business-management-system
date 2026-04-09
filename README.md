# SME Business Management System

<p align="center">
  <img src="https://img.shields.io/badge/Frontend-Vercel-black?style=for-the-badge&logo=vercel" />
  <img src="https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render" />
  <img src="https://img.shields.io/badge/Database-Neon-00E699?style=for-the-badge&logo=postgresql" />
  <img src="https://img.shields.io/badge/Stack-React%20%7C%20Django%20%7C%20PostgreSQL-blue?style=for-the-badge" />
</p>

<p align="center">
  A production-style full-stack business management application for small and medium businesses in Tanzania.
</p>

<p align="center">
  <a href="https://sme-business-management-system.vercel.app"><strong>Live Demo</strong></a> •
  <a href="https://sme-business-management-system.onrender.com"><strong>Backend API</strong></a>
</p>

---

## Overview

SME Business Management System is a full-stack web application designed to help small and medium businesses manage their day-to-day operations digitally.

It is suitable for businesses such as:

- shops
- salons
- boutiques
- pharmacies
- stationery stores

The system helps track products, stock, sales, expenses, customers, debts, payments, and reports from one place.

---

## Live Links

- **Frontend:** https://sme-business-management-system.vercel.app
- **Backend:** https://sme-business-management-system.onrender.com

---

## Demo Credentials

### Admin
- **Username:** `admin`
- **Password:** `demo1234`

### Cashier
- **Username:** `cashier`
- **Password:** `demo1234`

### Store Keeper
- **Username:** `storekeeper`
- **Password:** `demo1234`

---

## Features

- Role-based authentication
- Dashboard with key performance summaries
- Product management
- Category management
- Inventory tracking
- Sales management
- Expense tracking
- Customer management
- Debt tracking with partial payments
- Payment records
- Reports and analytics
- Tanzanian business-focused structure

---

## User Roles

| Role | Description |
|------|-------------|
| Admin | Full access to the entire system |
| Cashier | Handles sales and payment activities |
| Store Keeper | Manages stock and inventory updates |

---

## Core Modules

### Authentication
Secure login system with access control based on user roles.

### Dashboard
Displays important summaries such as:
- total sales
- total expenses
- low-stock products
- debts
- recent activities

### Product Management
Manage products with details such as:
- product name
- category
- buying price
- selling price
- quantity
- reorder level
- description

### Category Management
Create, edit, and organize product categories.

### Inventory Management
Track:
- stock in
- stock out
- stock movement history
- automatic quantity updates after sales

### Sales Management
Supports:
- multi-item sales
- receipt-friendly transactions
- amount paid and balance calculation
- transaction history

### Expense Management
Record and track business expenses.

### Customer Management
Store customer information and view customer transaction history.

### Debt Management
Track:
- unpaid balances
- partial payments
- remaining amounts
- cleared debts

### Payment Records
Supports payment methods such as:
- cash
- mobile money
- bank transfer

### Reports
Generate insights for:
- sales
- expenses
- debts
- stock
- top-selling products

---

## Tech Stack

### Frontend
- React
- Vite
- CSS

### Backend
- Django
- Django REST Framework

### Database
- PostgreSQL (Neon)

### Deployment
- Vercel
- Render
- Neon

---

## Project Structure

```text
backend/
  config/
  business/
    management/commands/seed_demo.py
  manage.py
  requirements.txt

frontend/
  src/
    api/
    components/
    hooks/
    pages/
    styles/

README.md
