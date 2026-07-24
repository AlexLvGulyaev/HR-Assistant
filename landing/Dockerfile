# HR Assistant LoRA Landing - Production Dockerfile
FROM nginx:alpine

# Copy static landing assets into nginx web root
COPY . /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
