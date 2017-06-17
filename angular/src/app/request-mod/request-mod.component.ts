import { Component, OnInit } from '@angular/core';

import { ServerService } from '../service/server.service';
import { Router } from "@angular/router"

import { CookieService } from 'angular2-cookie/core';

@Component({
  selector: 'app-request-mod',
  templateUrl: './request-mod.component.html',
  styleUrls: ['./request-mod.component.sass']
})
export class RequestModComponent implements OnInit {
  reason: string;
  answer: string;
  errorMessage: string;
  available: boolean;
  loading = true;


  constructor(private server: ServerService) {}

  check_request() {
    this.server.get("user/can_request_mod", true)
      .then(answer => {
        if (answer['requested_mod'])
          this.available = false;
        else
          this.available = true;
        this.loading = false;
      })
      .catch(error => {
        this.available = false
        this.loading = false;
      });

  }

  send_request(){
    if (!this.available)
      return -1;
    let request = {reason: this.reason}
    this.server.post("user/request_mod", request)
      .then(answer => {this.answer = answer;
                        this.available=false})
      .catch(error => this.errorMessage = error.statusText);
  }

  ngOnInit() {
    this.check_request();
  }

}
