-- =============================================================================
-- FitHer Gym Manager — Database Schema
-- Database: fither_gym
-- MySQL 8.0+
-- =============================================================================
-- Run this file in MySQL Workbench or the MySQL CLI after creating the database.
-- Safe to run multiple times: uses IF NOT EXISTS and INSERT IGNORE.
-- =============================================================================

CREATE DATABASE IF NOT EXISTS fither_gym
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE fither_gym;

-- ---------------------------------------------------------------------------
-- Table A: members
-- Stores basic personal information for each gym member.
-- Gender defaults to 'Female' because this is a female-only gym.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS members (
    member_id   INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    full_name   VARCHAR(150)    NOT NULL,
    phone       VARCHAR(20)     NOT NULL,
    joining_date DATE           NOT NULL,
    gender      ENUM('Female','Male','Other') NOT NULL DEFAULT 'Female',
    notes       TEXT            NULL,
    created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (member_id),
    INDEX idx_members_phone (phone),
    INDEX idx_members_name  (full_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------------
-- Table B: membership_plans
-- Defines the available membership packages.
-- Prices are in Pakistani Rupees (PKR) stored as exact DECIMAL.
-- is_active = 1 means the plan is currently offered; 0 means retired.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS membership_plans (
    plan_id          INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    plan_name        VARCHAR(100)  NOT NULL,
    duration_months  TINYINT UNSIGNED NOT NULL CHECK (duration_months > 0),
    price            DECIMAL(10,2) NOT NULL,
    description      TEXT          NULL,
    is_active        TINYINT(1)    NOT NULL DEFAULT 1,

    PRIMARY KEY (plan_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------------
-- Table C: subscriptions
-- Records each time a member is enrolled in a plan.
-- A member may have many subscriptions over time (renewals create new rows).
--
-- Date convention:
--   start_date is inclusive (the member starts using the gym on this day).
--   end_date   is inclusive (the last day of the membership period).
--   Example: start 2024-10-10, 1 month → end 2024-11-09.
--
-- Status field: 'active' | 'expired' | 'cancelled'
--   The application always re-derives the live status from today's date and
--   the date range.  The stored status is updated as a convenience label but
--   is NOT the authoritative source for whether a subscription is active.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    member_id       INT UNSIGNED   NOT NULL,
    plan_id         INT UNSIGNED   NOT NULL,
    start_date      DATE           NOT NULL,
    end_date        DATE           NOT NULL,
    agreed_fee      DECIMAL(10,2)  NOT NULL,
    status          ENUM('active','expired','cancelled') NOT NULL DEFAULT 'active',
    created_at      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (subscription_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)   ON DELETE RESTRICT,
    FOREIGN KEY (plan_id)   REFERENCES membership_plans(plan_id) ON DELETE RESTRICT,
    INDEX idx_subscriptions_member   (member_id),
    INDEX idx_subscriptions_end_date (end_date),
    INDEX idx_subscriptions_status   (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------------
-- Table D: payments
-- Records individual payment transactions against a subscription.
-- A subscription may have multiple payments (partial payments supported).
-- Outstanding balance = agreed_fee − SUM(amount) for the subscription.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    payment_id      INT UNSIGNED   NOT NULL AUTO_INCREMENT,
    subscription_id INT UNSIGNED   NOT NULL,
    amount          DECIMAL(10,2)  NOT NULL,
    payment_date    DATE           NOT NULL,
    payment_method  ENUM('Cash','Bank Transfer','Other') NOT NULL DEFAULT 'Cash',
    notes           TEXT           NULL,
    created_at      TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (payment_id),
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id) ON DELETE RESTRICT,
    INDEX idx_payments_subscription (subscription_id),
    INDEX idx_payments_date         (payment_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------------
-- Seed data: default membership plans (fictional PKR prices for demo)
-- INSERT IGNORE prevents duplicate rows if this file is run again.
-- ---------------------------------------------------------------------------
INSERT IGNORE INTO membership_plans (plan_id, plan_name, duration_months, price, description, is_active) VALUES
(1, 'Monthly Membership',       1, 2500.00, 'Full gym access for one month. Perfect for trying out.',   1),
(2, 'Three-Month Membership',   3, 6500.00, 'Three months of full access with a small discount.',        1),
(3, 'Six-Month Membership',     6, 11000.00,'Six months of full access — best value for regular members.',1),
(4, 'Student Monthly',          1, 1800.00, 'Discounted monthly plan for students (ID required).',       1);
