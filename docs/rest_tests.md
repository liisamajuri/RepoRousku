# REST API Dokumentaatio

Tämä dokumentaatio sisältää yleiskuvauksen .rest-testitiedostoista. Tarkempi Swagger-dokumentaatio löytyy [täältä](http://localhost:8088/docs).

## clockify_requests.rest

Tämä tiedosto sisältää REST-pyynnöt Clockify-integraation testaamiseksi RepoRouskun API:ssa.

| Pyyntö | Kuvaus |
|---|---|
| GET ```/api/v1/clockify/workspaces``` | Hae kaikki työtilat |
| GET ```/api/v1/clockify/workspaces/{workspaceId}/projects``` | Hae työtilan projektit |
| GET ```/api/v1/clockify/workspaces/{workspaceId}/projects/{projectId}/users``` | Hae kaikkien käyttäjien työtunnit projektista |
| GET ```/api/v1/clockify/workspaces/{workspaceId}/projects/{projectId}/users/{userId}/time-entries``` | Hae yksittäisen käyttäjän aikakirjaukset projektista |
| GET ```/api/v1/clockify/workspaces/{workspaceId}/projects/{projectId}/total-hours``` | Hae projektin kokonaistunnit |
| GET ```/api/v1/clockify/workspaces/{workspaceId}/projects/{projectId}/users/{userId}/total-hours``` | Hae käyttäjän kokonaistunnit projektissa |

## functionality_check.rest

Tämä tiedosto sisältää REST-pyynnöt API-rajapinnan yleisen toimivuuden testaamiseksi RepoRouskun API:ssa.

| Pyyntö | Kuvaus |
|---|---|
| GET ```/health``` | Tarkista API:n toimivuus |
| GET ```/status``` | Tarkista API:n status |

## gitlab_requests.rest

Tämä tiedosto sisältää REST-pyynnöt GitLab-integraation testaamiseksi RepoRouskun API:ssa.

| Pyyntö | Kuvaus |
|---|---|
| GET ```/api/v1/gitlab/project-summary?project_url={projectUrl}``` | Hae GitLab-projektin yleiset tiedot |
| GET ```/api/v1/gitlab/member-summary?project_url={projectUrl}&member={memberName}``` | Hae GitLab-projektin jäsenen tilastot |

