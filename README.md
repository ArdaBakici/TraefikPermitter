# TraefikPermitter - A Solution For Dynamic IP Based Whitelist for [Traefik](https://github.com/traefik/traefik)

TraefikPermitter is an web-app for [Traefik](https://github.com/traefik/traefik) that allows your users to add themselves to IP-based whitelist.

TraefikPermitter is an basic Flask based web app that changes the rule file for Traefik. Current repo has examples for an Minecraft server.

Caution: TraefikPermitter itself doesn't include an authentication agent due to possible security concerns. Instead it should be used with Authelia or Authentik to limit which users can add themselves to the whitelist.

Current example uses Authelia as a middleware for authentication.
