import { sql } from "drizzle-orm";
import { pgTable, text, varchar, integer, boolean, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const countries = pgTable("countries", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  code: text("code").notNull().unique(),
  flag: text("flag").notNull(),
  priceFrom: integer("price_from").notNull(),
  available: boolean("available").notNull().default(true),
  numbersCount: integer("numbers_count").notNull().default(0),
  status: text("status").notNull().default("available"), // available, low, unavailable
});

export const services = pgTable("services", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  icon: text("icon").notNull(),
  priceFrom: integer("price_from").notNull(),
  priceTo: integer("price_to").notNull(),
  available: boolean("available").notNull().default(true),
});

export const orders = pgTable("orders", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  phoneNumber: text("phone_number").notNull(),
  countryId: varchar("country_id").references(() => countries.id).notNull(),
  serviceId: varchar("service_id").references(() => services.id).notNull(),
  price: integer("price").notNull(),
  status: text("status").notNull().default("active"), // active, completed, expired
  expiresAt: timestamp("expires_at").notNull(),
  createdAt: timestamp("created_at").notNull().default(sql`now()`),
});

export const messages = pgTable("messages", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  orderId: varchar("order_id").references(() => orders.id).notNull(),
  text: text("text").notNull(),
  code: text("code"),
  receivedAt: timestamp("received_at").notNull().default(sql`now()`),
});

export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  telegramId: text("telegram_id").notNull().unique(),
  username: text("username"),
  balance: integer("balance").notNull().default(0), // in kopecks
  isAdmin: boolean("is_admin").notNull().default(false),
});

export const settings = pgTable("settings", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  key: text("key").notNull().unique(),
  value: text("value").notNull(),
  description: text("description"),
  updatedAt: timestamp("updated_at").notNull().default(sql`now()`),
});

export const statistics = pgTable("statistics", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  date: text("date").notNull(), // YYYY-MM-DD
  totalOrders: integer("total_orders").notNull().default(0),
  totalRevenue: integer("total_revenue").notNull().default(0), // in kopecks
  newUsers: integer("new_users").notNull().default(0),
  activeUsers: integer("active_users").notNull().default(0),
});

export const insertCountrySchema = createInsertSchema(countries).omit({
  id: true,
});

export const insertServiceSchema = createInsertSchema(services).omit({
  id: true,
});

export const insertOrderSchema = createInsertSchema(orders).omit({
  id: true,
  createdAt: true,
});

export const insertMessageSchema = createInsertSchema(messages).omit({
  id: true,
  receivedAt: true,
});

export const insertUserSchema = createInsertSchema(users).omit({
  id: true,
});

export const insertSettingSchema = createInsertSchema(settings).omit({
  id: true,
  updatedAt: true,
});

export const insertStatisticSchema = createInsertSchema(statistics).omit({
  id: true,
});

export type Country = typeof countries.$inferSelect;
export type Service = typeof services.$inferSelect;
export type Order = typeof orders.$inferSelect;
export type Message = typeof messages.$inferSelect;
export type User = typeof users.$inferSelect;
export type Setting = typeof settings.$inferSelect;
export type Statistic = typeof statistics.$inferSelect;
export type InsertCountry = z.infer<typeof insertCountrySchema>;
export type InsertService = z.infer<typeof insertServiceSchema>;
export type InsertOrder = z.infer<typeof insertOrderSchema>;
export type InsertMessage = z.infer<typeof insertMessageSchema>;
export type InsertUser = z.infer<typeof insertUserSchema>;
export type InsertSetting = z.infer<typeof insertSettingSchema>;
export type InsertStatistic = z.infer<typeof insertStatisticSchema>;
