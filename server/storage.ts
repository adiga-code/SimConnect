import { type Country, type Service, type Order, type Message, type User, type InsertCountry, type InsertService, type InsertOrder, type InsertMessage, type InsertUser } from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  // Countries
  getCountries(): Promise<Country[]>;
  getCountry(id: string): Promise<Country | undefined>;
  
  // Services
  getServices(): Promise<Service[]>;
  getService(id: string): Promise<Service | undefined>;
  
  // Orders
  getOrders(): Promise<Order[]>;
  getOrdersByStatus(status: string): Promise<Order[]>;
  createOrder(order: InsertOrder): Promise<Order>;
  
  // Messages
  getMessagesByOrderId(orderId: string): Promise<Message[]>;
  getAllMessages(): Promise<Message[]>;
  createMessage(message: InsertMessage): Promise<Message>;
  
  // Users
  getUser(telegramId: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  updateUserBalance(telegramId: string, balance: number): Promise<User | undefined>;
}

export class MemStorage implements IStorage {
  private countries: Map<string, Country>;
  private services: Map<string, Service>;
  private orders: Map<string, Order>;
  private messages: Map<string, Message>;
  private users: Map<string, User>;

  constructor() {
    this.countries = new Map();
    this.services = new Map();
    this.orders = new Map();
    this.messages = new Map();
    this.users = new Map();
    
    this.initializeMockData();
  }

  private initializeMockData() {
    // Initialize countries
    const countriesData: InsertCountry[] = [
      { name: "Россия", code: "RU", flag: "🇷🇺", priceFrom: 15, available: true, numbersCount: 1234, status: "available" },
      { name: "Украина", code: "UA", flag: "🇺🇦", priceFrom: 22, available: true, numbersCount: 856, status: "available" },
      { name: "Казахстан", code: "KZ", flag: "🇰🇿", priceFrom: 18, available: true, numbersCount: 12, status: "low" },
      { name: "США", code: "US", flag: "🇺🇸", priceFrom: 45, available: false, numbersCount: 0, status: "unavailable" },
    ];

    countriesData.forEach(country => {
      const id = randomUUID();
      this.countries.set(id, { ...country, id });
    });

    // Initialize services
    const servicesData: InsertService[] = [
      { name: "Telegram", icon: "fab fa-telegram", priceFrom: 15, priceTo: 25, available: true },
      { name: "WhatsApp", icon: "fab fa-whatsapp", priceFrom: 18, priceTo: 30, available: true },
      { name: "Discord", icon: "fab fa-discord", priceFrom: 20, priceTo: 35, available: true },
    ];

    servicesData.forEach(service => {
      const id = randomUUID();
      this.services.set(id, { ...service, id });
    });

    // Initialize sample user
    const sampleUser: InsertUser = {
      telegramId: "sample_user",
      username: "user",
      balance: 12550, // 125.50 rubles in kopecks
    };
    const userId = randomUUID();
    this.users.set(sampleUser.telegramId, { ...sampleUser, id: userId });

    // Initialize sample orders
    const countryIds = Array.from(this.countries.keys());
    const serviceIds = Array.from(this.services.keys());
    
    const ordersData: InsertOrder[] = [
      {
        phoneNumber: "+7 916 123-45-67",
        countryId: countryIds[0],
        serviceId: serviceIds[0],
        price: 18,
        status: "active",
        expiresAt: new Date(Date.now() + 15 * 60 * 1000), // 15 minutes from now
      },
      {
        phoneNumber: "+7 916 987-65-43",
        countryId: countryIds[0],
        serviceId: serviceIds[0],
        price: 15,
        status: "completed",
        expiresAt: new Date(Date.now() - 10 * 60 * 1000), // 10 minutes ago
      },
    ];

    ordersData.forEach(order => {
      const id = randomUUID();
      const orderWithId = { ...order, id, createdAt: new Date() };
      this.orders.set(id, orderWithId);
    });

    // Initialize sample messages
    const orderIds = Array.from(this.orders.keys());
    const messagesData: InsertMessage[] = [
      {
        orderId: orderIds[0],
        text: "Ваш код подтверждения: 12345",
        code: "12345",
      },
      {
        orderId: orderIds[1],
        text: "Your WhatsApp code: 67890",
        code: "67890",
      },
    ];

    messagesData.forEach(message => {
      const id = randomUUID();
      this.messages.set(id, { ...message, id, receivedAt: new Date() });
    });
  }

  async getCountries(): Promise<Country[]> {
    return Array.from(this.countries.values());
  }

  async getCountry(id: string): Promise<Country | undefined> {
    return this.countries.get(id);
  }

  async getServices(): Promise<Service[]> {
    return Array.from(this.services.values());
  }

  async getService(id: string): Promise<Service | undefined> {
    return this.services.get(id);
  }

  async getOrders(): Promise<Order[]> {
    return Array.from(this.orders.values()).sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }

  async getOrdersByStatus(status: string): Promise<Order[]> {
    return Array.from(this.orders.values())
      .filter(order => order.status === status)
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
  }

  async createOrder(insertOrder: InsertOrder): Promise<Order> {
    const id = randomUUID();
    const order: Order = { 
      ...insertOrder, 
      id, 
      createdAt: new Date(),
    };
    this.orders.set(id, order);
    return order;
  }

  async getMessagesByOrderId(orderId: string): Promise<Message[]> {
    return Array.from(this.messages.values())
      .filter(message => message.orderId === orderId)
      .sort((a, b) => new Date(b.receivedAt).getTime() - new Date(a.receivedAt).getTime());
  }

  async getAllMessages(): Promise<Message[]> {
    return Array.from(this.messages.values())
      .sort((a, b) => new Date(b.receivedAt).getTime() - new Date(a.receivedAt).getTime());
  }

  async createMessage(insertMessage: InsertMessage): Promise<Message> {
    const id = randomUUID();
    const message: Message = { 
      ...insertMessage, 
      id, 
      receivedAt: new Date(),
    };
    this.messages.set(id, message);
    return message;
  }

  async getUser(telegramId: string): Promise<User | undefined> {
    return this.users.get(telegramId);
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { ...insertUser, id };
    this.users.set(insertUser.telegramId, user);
    return user;
  }

  async updateUserBalance(telegramId: string, balance: number): Promise<User | undefined> {
    const user = this.users.get(telegramId);
    if (user) {
      user.balance = balance;
      this.users.set(telegramId, user);
      return user;
    }
    return undefined;
  }
}

export const storage = new MemStorage();
