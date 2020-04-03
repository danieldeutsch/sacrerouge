lines = open('ROUGE-BEwTE/pom.xml', 'r').read().splitlines()
with open('ROUGE-BEwTE/pom.xml', 'w') as out:
    for line in lines[:80]:
        out.write(line + '\n')
    out.write('''
        <plugin>
            <groupId>org.codehaus.mojo</groupId>
            <artifactId>exec-maven-plugin</artifactId>
            <version>1.6.0</version>
            <executions>
              <execution>
                <id>RunPipe</id>
                <configuration>
                  <mainClass>tratz.runpipe.util.RunPipe</mainClass>
                </configuration>
              </execution>
              <execution>
                <id>BEXpander</id>
                <configuration>
                  <mainClass>bewte.BEXpander</mainClass>
                </configuration>
              </execution>
              <execution>
                <id>BEwT_E</id>
                <configuration>
                  <mainClass>bewte.BEwT_E</mainClass>
                </configuration>
              </execution>
            </executions>
        </plugin>
    ''')
    for line in lines[80:]:
        out.write(line + '\n')
