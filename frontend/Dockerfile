# Stage 1: Build React/Vite production assets
FROM node:20-alpine AS build

WORKDIR /app

# Copy package configurations and install dependencies
COPY package*.json ./
RUN npm install

# Copy the frontend application code and build static assets
COPY . .
RUN npm run build

# Stage 2: Serve the compiled static assets using a high-performance Nginx server
FROM nginx:stable-alpine

# Copy the built assets from the previous stage to the Nginx serving directory
COPY --from=build /app/dist /usr/share/nginx/html

# Expose Nginx standard port
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]