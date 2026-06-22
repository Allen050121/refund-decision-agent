FROM openjdk:21-slim

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline

COPY src ./src

RUN mvn package -DskipTests

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "target/aftersale-service-0.0.1-SNAPSHOT.jar"]
