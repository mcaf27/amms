from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import re
import pandas as pd
from numpy import random
import time

df = pd.read_csv('livros.csv', index_col='Link Skoob', encoding='utf-8')

driver = webdriver.Chrome()


def close_popup():
    time.sleep(3 + random.random())
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.modal-body')))
    driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.ESCAPE)


def get_book_info():
    book_info = {'Link Skoob': link, 'Nome': name}

    try:
        sidebar = driver.find_element(
            By.CSS_SELECTOR, '#pg-livro-menu-principal-container')

        author = sidebar.find_element(
            By.CSS_SELECTOR, "a[href^='/autor/']").text
        book_info['Autor'] = author

        summary = driver.find_element(
            By.CSS_SELECTOR, '#livro-perfil-sinopse-txt p').text
        print(summary)

        summary = summary.strip().replace('\n', ' ').replace('"', "'")
        # if len(summary) and summary[0] != '"':
        #     print('0', summary[0])
        #     summary = f'{summary}'
        print(summary)
        book_info['Sinopse'] = summary

    except NoSuchElementException:
        book_info['Autor'] = ''
        book_info['Sinopse'] = ''

    return book_info


with open('dados.csv', 'a+') as f:
    for index, row in df.head(551)[~df.head(551)['Coletado?'].astype(bool)].iterrows():
        try:
            name = row['Nome']
            if ',' in name:
                name = f'"{name}"'
            link = row.name

            driver.get(link)
            close_popup()

            # find similar books

            # similar_books_link = driver.find_element(
            #     By.CSS_SELECTOR, "a[href^='/livro/similares']")
            # # botão escondido por aviso de cookies
            # driver.execute_script("arguments[0].click();", similar_books_link)
            # close_popup()

            # container = WebDriverWait(driver, 30).until(
            #     EC.presence_of_element_located(
            #         (By.CSS_SELECTOR, '#resultadoBusca div'))
            # )

            # similar_books = container.find_elements(
            #     By.CSS_SELECTOR, 'div div.similar-book a')
            # for book in similar_books:
            #     similar_link = book.get_attribute('href')
            #     title = book.get_attribute('title')
            #     if similar_link in df.index:
            #         continue
            #     else:
            #         df.loc[similar_link] = {'Nome': title, 'Coletado?': False}

            # get readers & book info

            # driver.get(link)
            # close_popup()

            book_info = {'Link Skoob': link, 'Nome': name}

            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '#pg-livro-menu-principal-container')))
                sidebar = driver.find_element(
                    By.CSS_SELECTOR, '#pg-livro-menu-principal-container')

                author_link = sidebar.find_elements(
                    By.CSS_SELECTOR, "a[href^='/autor/']")
                if len(author_link) > 0:
                    book_info['Autor'] = author_link[0].text
                else:
                    author_text = sidebar.find_elements(
                        By.CSS_SELECTOR, "i.sidebar-subtitulo")
                    if len(author_text) > 0:
                        book_info['Autor'] = author_text[0].text
                    else:
                        raise NoSuchElementException

                summary = driver.find_element(
                    By.CSS_SELECTOR, '#livro-perfil-sinopse-txt p').text
                # print(summary)

                summary = summary.strip().replace('\n', ' ').replace('"', "'")
                # if len(summary) and summary[0] != '"':
                #     summary = f'"{summary}"'
                book_info['Sinopse'] = summary

            except NoSuchElementException:
                book_info['Autor'] = ''
                book_info['Sinopse'] = ''

            readers_link = driver.find_element(
                By.CSS_SELECTOR, "div.bar a[href^='/livro/leitores/leram']")
            time.sleep(3 + random.random())
            readers_link.click()
            close_popup()

            readers = []

            while True:
                try:
                    readers_page = driver.find_element(
                        By.CSS_SELECTOR, "div#livro-leitores-box")
                    a_tags = readers_page.find_elements(
                        By.CSS_SELECTOR, "div a")

                    for a_tag in a_tags:
                        href = a_tag.get_attribute("href")
                        reader = re.search(
                            r'https://www\.skoob\.com\.br/usuario/(\d+)-', href).group(1)
                        if href:
                            readers.append(reader)

                    next_button = driver.find_element(
                        By.CSS_SELECTOR, '.paginacao_lista_busca .proximo a')
                    next_button.click()
                    close_popup()

                except NoSuchElementException:
                    break

            f.write(
                f"{book_info['Nome']},{book_info['Autor']},\"{book_info['Sinopse']}\"," + ';'.join(readers) + '\n')
            df.loc[link, 'Coletado?'] = True
            print('<', book_info['Nome'])
        except Exception as e:
            print('Exceção:', e)

df.to_csv('livros.csv', index=True)

input('\nFechar...')

driver.close()
