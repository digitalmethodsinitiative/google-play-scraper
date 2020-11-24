Feature: scraper intial

  Scenario: run a simple search
     Given we have play store scraper installed
      When we search for "racism"
      Then the scraper will return "50" results

  Scenario: run a similarity search
     Given we have play store scraper installed
      When we search for result from "mindful"
      Then the scraper will return "14" results

  Scenario: run a collections search
     Given we have play store scraper installed
      When we search for the topic "topselling_free"
      Then the scraper will return "10" results

  Scenario: run a developer search
     Given we have play store scraper installed
      When we search for the developer "Headspace for Meditation, Mindfulness and Sleep"
      Then the scraper will return "1" results

  Scenario: run an app search
     Given we have play store scraper installed
      When we search for the app with id "io.mindnow.mindful"
      Then the results length is "19"

  Scenario: run a multiple app search
     Given we have play store scraper installed
      When we search for "10" apps
      Then the scraper will return "10" results

  Scenario: run a multiple app search with incorrect app id
     Given we have play store scraper installed
     When we define an incorrect app id "872"
      And we search for another "10" apps
      Then the scraper will return "10" results
