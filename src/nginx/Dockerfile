FROM nginx:1.20-alpine
RUN rm /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/
COPY backend.conf /etc/nginx/conf.d
