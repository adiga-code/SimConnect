import { type Country, type Service, type Order, type Message, type User, type Setting, type Statistic, type InsertCountry, type InsertService, type InsertOrder, type InsertMessage, type InsertUser, type InsertSetting, type InsertStatistic } from "@shared/schema";
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
  
  // Settings
  getSettings(): Promise<Setting[]>;
  getSetting(key: string): Promise<Setting | undefined>;
  updateSetting(key: string, value: string): Promise<Setting>;
  
  // Statistics
  getStatistics(): Promise<Statistic[]>;
  getStatisticsByDateRange(startDate: string, endDate: string): Promise<Statistic[]>;
  createOrUpdateStatistic(statistic: InsertStatistic): Promise<Statistic>;
}

export class MemStorage implements IStorage {
  private countries: Map<string, Country>;
  private services: Map<string, Service>;
  private orders: Map<string, Order>;
  private messages: Map<string, Message>;
  private users: Map<string, User>;
  private settings: Map<string, Setting>;
  private statistics: Map<string, Statistic>;

  constructor() {
    this.countries = new Map();
    this.services = new Map();
    this.orders = new Map();
    this.messages = new Map();
    this.users = new Map();
    this.settings = new Map();
    this.statistics = new Map();
    
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
      this.countries.set(id, { 
        ...country, 
        id,
        available: country.available ?? true,
        numbersCount: country.numbersCount ?? 0,
        status: country.status ?? "available"
      });
    });

    // Initialize services
    const servicesData: InsertService[] = [
      { name: "Telegram", icon: "fab fa-telegram", priceFrom: 15, priceTo: 25, available: true },
      { name: "WhatsApp", icon: "fab fa-whatsapp", priceFrom: 18, priceTo: 30, available: true },
      { name: "Discord", icon: "fab fa-discord", priceFrom: 20, priceTo: 35, available: true },
    ];

    servicesData.forEach(service => {
      const id = randomUUID();
      this.services.set(id, { 
        ...service, 
        id,
        available: service.available ?? true 
      });
    });

    // Initialize sample user
    const sampleUser: InsertUser = {
      telegramId: "sample_user",
      username: "user",
      balance: 12550, // 125.50 rubles in kopecks
      isAdmin: true,
    };
    const userId = randomUUID();
    this.users.set(sampleUser.telegramId, { 
      ...sampleUser, 
      id: userId,
      username: sampleUser.username ?? null,
      balance: sampleUser.balance ?? 0,
      isAdmin: sampleUser.isAdmin ?? false
    });

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
      const orderWithId = { 
        ...order, 
        id, 
        createdAt: new Date(),
        status: order.status ?? "active"
      };
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
      this.messages.set(id, { 
        ...message, 
        id, 
        receivedAt: new Date(),
        code: message.code ?? null
      });
    });

    // Initialize settings
    const settingsData = [
      { key: "commission_percent", value: "5", description: "Комиссия в процентах" },
      { key: "min_balance", value: "100", description: "Минимальный баланс в копейках" },
      { key: "support_url", value: "https://t.me/support", description: "Ссылка на техподдержку" },
      { key: "telegram_channel", value: "https://t.me/onlinesim_channel", description: "Ссылка на канал Telegram" },
    ];

    settingsData.forEach(setting => {
      const id = randomUUID();
      this.settings.set(setting.key, { ...setting, id, updatedAt: new Date() });
    });

    // Initialize statistics
    const today = new Date().toISOString().split('T')[0];
    const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    const statisticsData = [
      { date: today, totalOrders: 45, totalRevenue: 125000, newUsers: 12, activeUsers: 89 },
      { date: yesterday, totalOrders: 38, totalRevenue: 98500, newUsers: 8, activeUsers: 76 },
    ];

    statisticsData.forEach(stat => {
      const id = randomUUID();
      this.statistics.set(stat.date, { ...stat, id });
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
      status: insertOrder.status ?? "active"
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
      code: insertMessage.code ?? null
    };
    this.messages.set(id, message);
    return message;
  }

  async getUser(telegramId: string): Promise<User | undefined> {
    return this.users.get(telegramId);
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { 
      ...insertUser, 
      id,
      username: insertUser.username ?? null,
      balance: insertUser.balance ?? 0,
      isAdmin: insertUser.isAdmin ?? false
    };
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

  async getSettings(): Promise<Setting[]> {
    return Array.from(this.settings.values());
  }

  async getSetting(key: string): Promise<Setting | undefined> {
    return this.settings.get(key);
  }

  async updateSetting(key: string, value: string): Promise<Setting> {
    const existing = this.settings.get(key);
    if (existing) {
      existing.value = value;
      existing.updatedAt = new Date();
      this.settings.set(key, existing);
      return existing;
    }
    
    const id = randomUUID();
    const setting: Setting = { id, key, value, description: null, updatedAt: new Date() };
    this.settings.set(key, setting);
    return setting;
  }

  async getStatistics(): Promise<Statistic[]> {
    return Array.from(this.statistics.values()).sort((a, b) => b.date.localeCompare(a.date));
  }

  async getStatisticsByDateRange(startDate: string, endDate: string): Promise<Statistic[]> {
    return Array.from(this.statistics.values())
      .filter(stat => stat.date >= startDate && stat.date <= endDate)
      .sort((a, b) => b.date.localeCompare(a.date));
  }

  async createOrUpdateStatistic(insertStatistic: InsertStatistic): Promise<Statistic> {
    const existing = this.statistics.get(insertStatistic.date);
    if (existing) {
      Object.assign(existing, insertStatistic);
      this.statistics.set(insertStatistic.date, existing);
      return existing;
    }
    
    const id = randomUUID();
    const statistic: Statistic = { 
      ...insertStatistic, 
      id,
      totalOrders: insertStatistic.totalOrders ?? 0,
      totalRevenue: insertStatistic.totalRevenue ?? 0,
      newUsers: insertStatistic.newUsers ?? 0,
      activeUsers: insertStatistic.activeUsers ?? 0
    };
    this.statistics.set(insertStatistic.date, statistic);
    return statistic;
  }
}

export const storage = new MemStorage();
