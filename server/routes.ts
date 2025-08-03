import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertOrderSchema, insertMessageSchema, insertUserSchema } from "@shared/schema";
import { z } from "zod";

export async function registerRoutes(app: Express): Promise<Server> {
  // Countries routes
  app.get("/api/countries", async (_req, res) => {
    try {
      const countries = await storage.getCountries();
      res.json(countries);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch countries" });
    }
  });

  app.get("/api/countries/:id", async (req, res) => {
    try {
      const country = await storage.getCountry(req.params.id);
      if (!country) {
        return res.status(404).json({ message: "Country not found" });
      }
      res.json(country);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch country" });
    }
  });

  // Services routes
  app.get("/api/services", async (_req, res) => {
    try {
      const services = await storage.getServices();
      res.json(services);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch services" });
    }
  });

  app.get("/api/services/:id", async (req, res) => {
    try {
      const service = await storage.getService(req.params.id);
      if (!service) {
        return res.status(404).json({ message: "Service not found" });
      }
      res.json(service);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch service" });
    }
  });

  // Orders routes
  app.get("/api/orders", async (req, res) => {
    try {
      const status = req.query.status as string;
      const orders = status 
        ? await storage.getOrdersByStatus(status)
        : await storage.getOrders();
      res.json(orders);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch orders" });
    }
  });

  const createOrderSchema = insertOrderSchema.extend({
    telegramId: z.string(),
  });

  app.post("/api/orders", async (req, res) => {
    try {
      const validation = createOrderSchema.safeParse(req.body);
      if (!validation.success) {
        return res.status(400).json({ message: "Invalid order data", errors: validation.error.issues });
      }

      const { telegramId, ...orderData } = validation.data;
      
      // Check user balance
      const user = await storage.getUser(telegramId);
      if (!user) {
        return res.status(404).json({ message: "User not found" });
      }

      if (user.balance < orderData.price) {
        return res.status(400).json({ message: "Insufficient balance" });
      }

      // Create order
      const order = await storage.createOrder(orderData);
      
      // Update user balance
      await storage.updateUserBalance(telegramId, user.balance - orderData.price);

      res.status(201).json(order);
    } catch (error) {
      res.status(500).json({ message: "Failed to create order" });
    }
  });

  // Messages routes
  app.get("/api/messages", async (req, res) => {
    try {
      const orderId = req.query.orderId as string;
      const messages = orderId 
        ? await storage.getMessagesByOrderId(orderId)
        : await storage.getAllMessages();
      res.json(messages);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch messages" });
    }
  });

  app.post("/api/messages", async (req, res) => {
    try {
      const validation = insertMessageSchema.safeParse(req.body);
      if (!validation.success) {
        return res.status(400).json({ message: "Invalid message data", errors: validation.error.issues });
      }

      const message = await storage.createMessage(validation.data);
      res.status(201).json(message);
    } catch (error) {
      res.status(500).json({ message: "Failed to create message" });
    }
  });

  // Users routes
  app.get("/api/users/:telegramId", async (req, res) => {
    try {
      const user = await storage.getUser(req.params.telegramId);
      if (!user) {
        return res.status(404).json({ message: "User not found" });
      }
      res.json(user);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch user" });
    }
  });

  app.post("/api/users", async (req, res) => {
    try {
      const validation = insertUserSchema.safeParse(req.body);
      if (!validation.success) {
        return res.status(400).json({ message: "Invalid user data", errors: validation.error.issues });
      }

      const existingUser = await storage.getUser(validation.data.telegramId);
      if (existingUser) {
        return res.json(existingUser);
      }

      const user = await storage.createUser(validation.data);
      res.status(201).json(user);
    } catch (error) {
      res.status(500).json({ message: "Failed to create user" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
