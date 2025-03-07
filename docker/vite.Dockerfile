FROM node:lts-alpine
USER root
RUN mkdir /app
RUN chown node:node /app
USER node
WORKDIR /app
ADD --chown=node:node package.json package-lock.json /app/
RUN npm ci
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "8638", "--strictPort"]
