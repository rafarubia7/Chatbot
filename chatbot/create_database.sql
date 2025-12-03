-- Script SQL para criar o banco de dados senAI e suas tabelas
-- Execute este script no MySQL para criar o banco de dados

-- Criar o banco de dados
CREATE DATABASE IF NOT EXISTS `senAI` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Usar o banco de dados
USE `senAI`;

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS `usuarios` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(100) NOT NULL UNIQUE,
    `nome` VARCHAR(100) NULL,
    `senha` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NULL,
    `telefone` VARCHAR(20) NULL,
    `data_nascimento` DATE NULL,
    `curso` VARCHAR(100) NULL,
    `bio` TEXT NULL,
    `avatar_path` VARCHAR(255) NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_username` (`username`),
    INDEX `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de chats
CREATE TABLE IF NOT EXISTS `chats` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `chat_id` VARCHAR(100) NOT NULL UNIQUE,
    `user_id` INT NULL,  -- Permite NULL para usuários anônimos
    `session_id` VARCHAR(100) NULL,  -- ID de sessão para usuários anônimos
    `title` VARCHAR(255) NOT NULL DEFAULT 'Nova Conversa',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE,
    INDEX `idx_chat_id` (`chat_id`),
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_session_id` (`session_id`),  -- Índice para busca por session_id
    INDEX `idx_updated_at` (`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de mensagens
CREATE TABLE IF NOT EXISTS `mensagens` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `chat_id` INT NOT NULL,
    `text` TEXT NOT NULL,
    `sender` VARCHAR(20) NOT NULL,
    `nome_usuario` VARCHAR(100) NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`chat_id`) REFERENCES `chats`(`id`) ON DELETE CASCADE,
    INDEX `idx_chat_id` (`chat_id`),
    INDEX `idx_created_at` (`created_at`),
    INDEX `idx_sender` (`sender`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Criar usuário MySQL para a aplicação (opcional, ajuste conforme necessário)
-- CREATE USER IF NOT EXISTS 'app_user'@'localhost' IDENTIFIED BY 'aluno';
-- GRANT ALL PRIVILEGES ON senAI.* TO 'app_user'@'localhost';
-- FLUSH PRIVILEGES;

